/*
*
*    André Dexheimer Carneiro 21/14/2021
*
*    The consumer will send as many interests as needed to get the specified payload, considering that the maximum 
*    payload per NDN packet is 8800 bytes.
*
*/
#include <ndn-cxx/face.hpp>
#include <iostream>
#include <chrono>
#include <ctime>
#include <libgen.h>
#include <thread>
#include <stdio.h>

#define N_DEFAULT_PAYLOAD_BYTES 8000
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
      void run(std::string strNode, std::string strTimestamp, std::string strQueueFileName);

   private:
      void onData(const Interest&, const Data& data)       const;
      void onNack(const Interest&, const lp::Nack& nack)   const;
      void onTimeout(const Interest& interest)             const;
      void logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp) const;
      void logResultWithSize(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const;
      void consumePacket(std::string strInterest);
      std::vector<C2_DATA> readDataQueue(std::string strHostName, std::string strFilePath);

   private:
      Face m_face;
      std::string m_strHostName;
      std::string m_strInterest;
      std::string m_strLogPath;
      std::string m_strTimestamp;
      std::chrono::steady_clock::time_point m_dtBegin;
};

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
   
   fprintf(stdout, "[Consumer::run] Running consumer with HostName=%s; QueueFile=%s\n", m_strHostName.c_str(), strQueueFileName.c_str());
   
   lstData = readDataQueue(strNode, strQueueFileName);
   for (i = 0; i < lstData.size(); i++){
      dataBuff = lstData[i];
      fprintf(stdout, "[Consumer::run] %d, Type=%d, ID=%d, Payload=%d, Prod=%s, Cons=%s\n", dataBuff.nTimeMs, dataBuff.nType, dataBuff.nId, dataBuff.nPayload, dataBuff.strProd, dataBuff.strCons);
   }

   fprintf(stdout, "[Consumer::run] Read a total of %d data packages\n", lstData.size());
   return;
}

// --------------------------------------------------------------------------------
//  consumePacket
//
//
// --------------------------------------------------------------------------------
void Consumer::consumePacket(std::string strInterest){
   Face face;
   Name interestName;
   Interest interest;

   ///////////////////////////////////////////////
   // Configure interest
   interestName = Name(strInterest);
   interest     = Interest(interestName);
   interest.setCanBePrefix(false);
   interest.setMustBeFresh(true);
   interest.setInterestLifetime(6_s); // The default is 4 seconds

   fprintf(stdout, "[Consumer::run] Sending interest=%s\n", strInterest.c_str());

   face.expressInterest(interest, bind(&Consumer::onData, this,   _1, _2),
      bind(&Consumer::onNack, this, _1, _2), bind(&Consumer::onTimeout, this, _1));

   // pocessEvents will block until the requested data is received or a timeout occurs
   face.processEvents();
}

// --------------------------------------------------------------------------------
//   onData
//
//
// --------------------------------------------------------------------------------
void Consumer::onData(const Interest& interest, const Data& data) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

   // logResult(sTimeDiff, "DATA", m_strTimestamp);
   logResultWithSize(sTimeDiff, "DATA", interest.getName().toUri(), m_strTimestamp, data.getContent().value_size());

   std::cout << "[Consumer::onData] Received Data=\n" << data << "Delay=" << sTimeDiff << "; Size=" << data.getContent().value_size() << std::endl;
}

// --------------------------------------------------------------------------------
//   onNack
//
//
// --------------------------------------------------------------------------------
void Consumer::onNack(const Interest& interest, const lp::Nack& nack) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

   logResult(sTimeDiff, "NACK", interest.getName().toUri(), m_strTimestamp);

   std::cout << "[Consumer::onNack] Received Nack interest=" << m_strInterest <<
      ";Reason=" << nack.getReason() << "Delay=" << sTimeDiff << std::endl;
}

// --------------------------------------------------------------------------------
//   onTimeout
//
//
// --------------------------------------------------------------------------------
void Consumer::onTimeout(const Interest& interest) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   std::cout << "[Consumer::onTimeout] Timeout for " << interest << std::endl;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

   logResult(sTimeDiff, "TIMEOUT", interest.getName().toUri(), m_strTimestamp);

   std::cout << "[Consumer::onTimeout] Timeout for interest=" << m_strInterest << "Delay="
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
    char  pLineBuff[1000];
    std::vector<C2_DATA> lstData;
    C2_DATA dataBuff;
    int nLine, nRead;

    pFile = fopen(strFilePath.c_str(), "r");
    if (pFile != NULL) {
        nLine = 0;
        nRead = 0;
        // while (fgets(pLineBuff, sizeof(pLineBuff), pFile) != NULL){
        while (nRead != -1){
            // Format '%d;Type=%d;Id=%d;Payload=%d;Prod=%s;Cons=%s'
            // %s reads space delimited strings, so it had to be replaced with %[^;]
            // fprintf(stdout, "Read line=%s", pLineBuff);
            nLine++;
            nRead = fscanf(pFile, "%d;Type=%d;Id=%d;Payload=%d;Prod=%[^;];Cons=%s", &dataBuff.nTimeMs, &dataBuff.nType, &dataBuff.nId, &dataBuff.nPayload, dataBuff.strProd, dataBuff.strCons);
            if ((nRead == 6) && (strcmp(strHostName.c_str(), dataBuff.strCons) == 0)){
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
void Consumer::logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp) const
{
   FILE* pFile;

   if (m_strHostName.length() > 0){
      // Write results to files
      pFile = fopen(m_strLogPath.c_str(), "a");

      if (pFile){
         fprintf(pFile, "%s;%.4f;%s;%s\n", strInterest.c_str(), sTimeDiff, pResult, strTimestamp.c_str());
         fclose(pFile);
      }
      else{
         std::cout << "[Consumer::log] ERROR opening output file for pResult=" << pResult
             << std::endl;
      }
   }
}

// --------------------------------------------------------------------------------
//   logResult
//
//
// --------------------------------------------------------------------------------
void Consumer::logResultWithSize(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const
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
