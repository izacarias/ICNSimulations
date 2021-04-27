/*
*
*    André Dexheimer Carneiro 21/14/2021
*
*    The consumer will send as many interests as needed to get the specified payload, considering that the maximum 
*    payload per NDN packet is 8800 bytes.
*
*/
#include <ndn-cxx/face.hpp>
#include <ndn-cxx/util/scheduler.hpp>
#include <boost/asio/io_service.hpp>
#include <iostream>
#include <chrono>
#include <ctime>
#include <libgen.h>
#include <stdio.h>
#include <sys/timeb.h>

#define N_MAX_PACKET_BYTES      8000

typedef struct {
    int nTimeMs;
    int nType;
    int nId;
    int nPayload;
    char strProd[10];
    char strCons[10];
} C2_DATA;

// Enclosing code in ndn simplifies coding (can also use `using namespace ndn`)
namespace ndn {
// Additional nested namespaces should be used to prevent/limit name conflicts
namespace examples {

class Consumer
{
   public:
      Consumer();
      void run(std::string strNode, std::string strTimestamp, std::string strQueueFileName);

   private:
      void delayedInterest(C2_DATA dataBuff);
      std::vector<C2_DATA> readDataQueue(std::string strHostName, std::string strFilePath);

      void onData(const Interest&, const Data& data, const std::chrono::steady_clock::time_point& dtBegin)     const;
      void onNack(const Interest&, const lp::Nack& nack, const std::chrono::steady_clock::time_point& dtBegin) const;
      void onTimeout(const Interest& interest, const std::chrono::steady_clock::time_point& dtBegin)           const;

      void logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const;
      void log(const char* strMessage);

   private:
      // Explicitly create io_service object, which will be shared between Face and Scheduler
      boost::asio::io_service m_ioService;
      Scheduler m_scheduler;

      Face m_face;
      std::string m_strHostName;
      std::string m_strLogPath;
      std::string m_strTimestamp;
};

// --------------------------------------------------------------------------------
//   Constructor
//
//
// --------------------------------------------------------------------------------
Consumer::Consumer() : m_face(m_ioService), m_scheduler(m_ioService){}

// --------------------------------------------------------------------------------
//   run
//
//
// --------------------------------------------------------------------------------
void Consumer::run(std::string strNode, std::string strTimestamp, std::string strQueueFileName)
{
   uint i;
   std::vector<C2_DATA> lstData;
   std::string strLog;
   C2_DATA dataBuff;
   char strBuff[200];
   struct timeb start, end;
   int nDiff;

   ////////////////////////////////////////////////
   // Read and validate input parameters
   m_strHostName  = strNode;
   m_strTimestamp = strTimestamp;

   if (m_strHostName.length() > 0)
      m_strLogPath = "/tmp/minindn/" + m_strHostName + "/consumer.log";
   else
      m_strLogPath = "/tmp/minindn/consumer.log";
   
   fprintf(stdout, "[Consumer::run] Running consumer with HostName=%s; QueueFile=%s\n", m_strHostName.c_str(), strQueueFileName.c_str());
   strLog = "[Consumer::run] Runing consumer " + m_strHostName + "; file=" + strQueueFileName + "; log=" + m_strLogPath;
   log(strLog.c_str());

   lstData = readDataQueue(strNode, strQueueFileName);
   fprintf(stdout, "[Consumer::run] Read a total of %d data packages from file=%s\n", (int) lstData.size(), strQueueFileName.c_str());
   snprintf(strBuff, sizeof(strBuff), "[Consumer::run] Read a total of %d data packages from file=%s", (int) lstData.size(), strQueueFileName.c_str());
   log(strBuff);

   ///////////////////////////////////////////
   // Scheadule data to be consumed
   // i = 0;
   // ftime(&start);
   // while(i < lstData.size()){   
   //    ftime(&end);
   //    nDiff = (int) (1000.0 * (end.time - start.time) + (end.millitm - start.millitm));
   //    if (nDiff >= lstData[i].nTimeMs){
   //       dataBuff = lstData[i];
   //       fprintf(stdout, "[Consumer::run] Scheadule at %dms, Type=%d, ID=%d, Payload=%d, Prod=%s\n", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd);
   //       // snprintf(strBuff, sizeof(strBuff), "[Consumer::run] Scheadule at %dms, Type=%d, ID=%d, Payload=%d, Prod=%s", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd);
   //       // log(strBuff);
   //       delayedInterest(dataBuff);
   //       i++;
   //    }
   // }
   for (i = 0; i < lstData.size(); i++){
      dataBuff = lstData[i];
      fprintf(stdout, "[Consumer::run] Scheadule at %dms, Type=%d, ID=%d, Payload=%d, Prod=%s\n", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd);
      snprintf(strBuff, sizeof(strBuff), "[Consumer::run] Scheadule at %dms, Type=%d, ID=%d, Payload=%d, Prod=%s", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd);
      log(strBuff);
      m_scheduler.schedule(boost::chrono::milliseconds(dataBuff.nTimeMs), [this, dataBuff] { delayedInterest(dataBuff); });
   }
   
   // m_ioService.run() will block until all events finished or m_ioService.stop() is called
   m_ioService.run();
   log("Done\n");
   return;
}

// --------------------------------------------------------------------------------
//   delayedInterest
//
//
// --------------------------------------------------------------------------------
void Consumer::delayedInterest(C2_DATA dataBuff){

   char strBuf[100], strPrefix[60];
   int i, nPackets, nPacketPayload;
   bool bHasLeftover;
   Name interestName;
   Interest interest;
   std::chrono::steady_clock::time_point dtBegin;

   snprintf(strPrefix, sizeof(strPrefix), "/ndn/%s-site/%s/C2Data-%d-Type%d", dataBuff.strProd, dataBuff.strProd, dataBuff.nId, dataBuff.nType);

   // Determine number of packets necessary to fulfill the interest
   nPackets     = dataBuff.nPayload / N_MAX_PACKET_BYTES;
   bHasLeftover = false;
   if ((dataBuff.nPayload % N_MAX_PACKET_BYTES) > 0){
      bHasLeftover = true;
      nPackets++;
   }

   // Express interest for all packets
   for (i = 0; i < nPackets; i++){

      if ((bHasLeftover) && (i+1 == nPackets)){
         // Last packet
         nPacketPayload = dataBuff.nPayload % N_MAX_PACKET_BYTES;
      }
      else{
         // Any other packet
         nPacketPayload = N_MAX_PACKET_BYTES;
      }

      snprintf(strBuf, sizeof(strBuf), "%s-%db-%dof%d", strPrefix, nPacketPayload, i+1, nPackets);
      fprintf(stdout, "[Consumer::delayedInterest] Expressing interest=%s (%d/%d)\n", strBuf, i+1, nPackets);

      dtBegin = std::chrono::steady_clock::now();
      interestName = Name(strBuf);
      interest     = Interest(interestName);
      interest.setCanBePrefix(false);
      interest.setMustBeFresh(true);
      interest.setInterestLifetime(6_s);

      m_face.expressInterest(interest,
                           bind(&Consumer::onData, this, _1, _2, dtBegin),
                           bind(&Consumer::onNack, this, _1, _2, dtBegin),
                           bind(&Consumer::onTimeout, this, _1, dtBegin));
   }
}

// --------------------------------------------------------------------------------
//   onData
//
//
// --------------------------------------------------------------------------------
void Consumer::onData(const Interest& interest, const Data& data, const std::chrono::steady_clock::time_point& dtBegin) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - dtBegin).count();

   logResult(sTimeDiff, "DATA", interest.getName().toUri(), m_strTimestamp, data.getContent().value_size());
   fprintf(stdout, "[Consumer::onData] Received data=%s; delay=%.2fms; size=%d bytes\n", interest.getName().toUri().c_str(), sTimeDiff/1000.0, (int) data.getContent().value_size());
}

// --------------------------------------------------------------------------------
//   onNack
//
//
// --------------------------------------------------------------------------------
void Consumer::onNack(const Interest& interest, const lp::Nack& nack, const std::chrono::steady_clock::time_point& dtBegin) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - dtBegin).count();

   logResult(sTimeDiff, "NACK", interest.getName().toUri(), m_strTimestamp, 0);
   fprintf(stdout, "[Consumer::onNack] Received nack for interest=%s; delay=%.2fms\n", interest.getName().toUri().c_str(), sTimeDiff/1000.0);
}

// --------------------------------------------------------------------------------
//   onTimeout
//
//
// --------------------------------------------------------------------------------
void Consumer::onTimeout(const Interest& interest, const std::chrono::steady_clock::time_point& dtBegin) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   std::cout << "[Consumer::onTimeout] Timeout for " << interest << std::endl;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - dtBegin).count();

   logResult(sTimeDiff, "TIMEOUT", interest.getName().toUri(), m_strTimestamp, 0);
   fprintf(stdout, "[Consumer::onTimeout] Received timeout for interest=%s; delay=%.2fms\n", interest.getName().toUri().c_str(), sTimeDiff/1000.0);   
}

// --------------------------------------------------------------------------------
//   readDataQueue
//
//
// --------------------------------------------------------------------------------
std::vector<C2_DATA> Consumer::readDataQueue(std::string strHostName, std::string strFilePath)
{
    FILE* pFile;
    std::vector<C2_DATA> lstData;
    C2_DATA dataBuff;
    int nLine, nRead;
    char strBuff[200];

    pFile = fopen(strFilePath.c_str(), "r");
    if (pFile != NULL) {
        nLine = 0;
        nRead = 0;
        while (nRead != -1){
            // Format '%d;Type=%d;Id=%d;Payload=%d;Prod=%s;Cons=%s'
            // %s reads space delimited strings, so it had to be replaced with %[^;]
            nLine++;
            nRead = fscanf(pFile, "%d;Type=%d;Id=%d;Payload=%d;Prod=%[^;];Cons=%s", &dataBuff.nTimeMs, &dataBuff.nType, &dataBuff.nId, &dataBuff.nPayload, dataBuff.strProd, dataBuff.strCons);
            if ((nRead == 6) && (strcmp(strHostName.c_str(), dataBuff.strCons) == 0) && (strcmp(strHostName.c_str(), dataBuff.strProd) != 0)){
                // Success, add to queue
                lstData.push_back(dataBuff);
            }
        }
        fprintf(stdout, "[Consumer::readDataQueue] Done reading file, read %d lines\n", nLine);
        fclose(pFile);
    }
    else{
        fprintf(stdout, "[Consumer::readDataQueue] Could not open file=%s\n", strFilePath.c_str());
    }
    return lstData;
}

// --------------------------------------------------------------------------------
//   logResult
//
//
// --------------------------------------------------------------------------------
void Consumer::logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const
{
   FILE* pFile;

   if (m_strHostName.length() > 0){
      // Write results to files
      pFile = fopen(m_strLogPath.c_str(), "a");

      if (pFile){
         fprintf(pFile, "%s;%.4f;%s;%s;%d\n", strInterest.c_str(), sTimeDiff, pResult, strTimestamp.c_str(), (int)nSize);
         fclose(pFile);
      }
      else{
         std::cout << "[Consumer::log] ERROR opening output file for pResult=" << pResult
             << std::endl;
      }
   }
}

void Consumer::log(const char* strMessage)
{
   FILE* pFile;

  // Write results to files
  pFile = fopen(m_strLogPath.c_str(), "a");

  if (pFile){
      fprintf(pFile, "%s\n", strMessage);
      fclose(pFile);
  }
  else{
      std::cout << "[Producer::log] ERROR opening output file" << std::endl;
  }
}

} // namespace examples
} // namespace ndn

int main(int argc, char** argv){

   std::string strNodeName;
   std::string strTimestamp;
   std::string strFileName;

   strNodeName  = "";
   strTimestamp = "";
   strFileName  = "";

   if (argc > 2){
      strNodeName = argv[1];
      strFileName = argv[2];
   }
   else{
      fprintf(stdout, "[main] Usage: consumer-with-queue <hostname> <queueFile> <?timestamp>\n");
      return -1;
   }

   // Optional argument, timestamp
   if (argc > 3)
      strTimestamp = argv[3];

   try {
      ndn::examples::Consumer consumer;
      consumer.run(strNodeName, strTimestamp, strFileName);
      return 0;
   }
   catch (const std::exception& e) {
      std::cerr << "[main] ERROR: " << e.what() << std::endl;
      return 1;
   }
}
