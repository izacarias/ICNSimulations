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
Consumer::Consumer()
   : m_face(m_ioService) // Create face with io_service object
   , m_scheduler(m_ioService)
   {
   }

// --------------------------------------------------------------------------------
//   run
//
//
// --------------------------------------------------------------------------------
void Consumer::run(std::string strNode, std::string strTimestamp, std::string strQueueFileName)
{
   uint i;
   std::vector<C2_DATA> lstData;
   C2_DATA dataBuff;

   ////////////////////////////////////////////////
   // Read and validate input parameters
   m_strHostName  = strNode;
   m_strTimestamp = strTimestamp;

   if (m_strHostName.length() > 0)
      m_strLogPath = "/tmp/minindn/" + m_strHostName + "/consumer.log";
   else
      m_strLogPath = "/tmp/minindn/consumer.log";
   
   fprintf(stdout, "[Consumer::run] Running consumer with HostName=%s; QueueFile=%s\n", m_strHostName.c_str(), strQueueFileName.c_str());

   lstData = readDataQueue(strNode, strQueueFileName);
   fprintf(stdout, "[Consumer::run] Read a total of %d data packages from file=%s\n", (int) lstData.size(), strQueueFileName.c_str());

   ///////////////////////////////////////////
   // Scheadule data to be consumed
   for (i = 0; i < lstData.size(); i++){
      dataBuff = lstData[i];
      fprintf(stdout, "[Consumer::run] Scheadule %d, Type=%d, ID=%d, Payload=%d, Prod=%s, Cons=%s\n", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd, dataBuff.strCons);
      m_scheduler.schedule(boost::chrono::milliseconds(dataBuff.nTimeMs), [this] { delayedInterest(dataBuff); });
   }
   
   // m_ioService.run() will block until all events finished or m_ioService.stop() is called
   m_ioService.run();
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

      fprintf(stdout, "[Consumer::run] Expressing %d/%d for interest=%s\n", i+1, nPackets, strBuf);
      snprintf(strBuf, sizeof(strBuf), "%s-%db-%dof%d", strPrefix, nPacketPayload, i+1, nPackets);

      dtBegin = std::chrono::steady_clock::now();
      interestName(strBuf);
      interest(interestName);
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
void onData(const Interest& interest, const Data& data, const std::chrono::steady_clock::time_point& dtBegin) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - dtBegin).count();

   logResult(sTimeDiff, "DATA", interest.getName().toUri(), m_strTimestamp, data.getContent().value_size());

   std::cout << "[Consumer::onData] Received Data=\n" << data << "Delay=" << sTimeDiff << "; Size=" << data.getContent().value_size() << std::endl;
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

   std::cout << "[Consumer::onNack] Received Nack interest=" << interest.getName().toUri() <<
      ";Reason=" << nack.getReason() << "Delay=" << sTimeDiff << std::endl;
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

   std::cout << "[Consumer::onTimeout] Timeout for interest=" << interest.getName().toUri() << "Delay="
      << sTimeDiff << std::endl;
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
        fprintf(stdout, "[Consumer::readDataQueue] Could not open file=%s for editing\n", strFilePath.c_str());
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
