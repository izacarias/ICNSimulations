/*
*
*    André Dexheimer Carneiro 27/04/2021
*
*    The consumer will send as many interests as needed to get the specified payload, considering that the maximum 
*    payload per NDN packet is 8800 bytes.
*
*    This consumer request data based on a queue in the format of a text file.
*
*    Congestion control is used to avoid overloading the network with packets.
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
} USER_DATA;

typedef struct {    
    int  nTimeMs;
    char strInterest[50];
    bool bReadyToSend;
} NDN_REQUEST;

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
      void delayedInterest(USER_DATA dataBuff);
      std::vector<USER_DATA> readDataQueue(std::string strHostName, std::string strFilePath);
      
      std::vector<NDN_REQUEST> interestQueueForDataList(std::vector<USER_DATA> lstUserData);
      void getInterestFilter(char* strInterest, size_t nSize, char* strProd, int nId, int nType, int nPayload, int nPacketNum, int nTotalPackets);
      void printNdnRequest(NDN_REQUEST request);
      char* ndnRequestToStr(NDN_REQUEST request);
      char* userDataToStr(USER_DATA userData);
      void printUserData(USER_DATA userData);

      void onData(const Interest&, const Data& data, const std::chrono::steady_clock::time_point& dtBegin)     const;
      void onNack(const Interest&, const lp::Nack& nack, const std::chrono::steady_clock::time_point& dtBegin) const;
      void onTimeout(const Interest& interest, const std::chrono::steady_clock::time_point& dtBegin)           const;

      void logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const;
      void log(const char* strMessage);

   private:
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
Consumer::Consumer(){}

// --------------------------------------------------------------------------------
//   run
//
//
// --------------------------------------------------------------------------------
void Consumer::run(std::string strNode, std::string strTimestamp, std::string strQueueFileName){

   uint i;
   char strBuff[200];
   std::string strLog;
   std::vector<NDN_REQUEST> lstRequests;
   std::vector<USER_DATA> lstData;

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

   lstRequests = interestQueueForDataList(lstData);

   for (i = 0; i < lstRequests.size(); i++){
      fprintf(stdout, "[Consumer::run] NDN request (%3d/%3d) = %s\n", i+1, (int)lstRequests.size(), ndnRequestToStr(lstRequests[i]));
   }

   snprintf(strBuff, sizeof(strBuff), "[Consumer::run] Scheadule %d transmissions\n", (int) lstData.size());
   log(strBuff);
   
   log("Done\n");
   return;
}

// --------------------------------------------------------------------------------
//   getInterestFilter
//
//
// --------------------------------------------------------------------------------
void Consumer::getInterestFilter(char* strInterest, size_t nSize, char* strProd, int nId, int nType, int nPayload, int nPacketNum, int nTotalPackets){
    
    char strPrefix[20];

    // Prefix - /ndn/<host>-site/<host>/
    snprintf(strPrefix, sizeof(strPrefix), "/ndn/%s-site/%s/", strProd, strProd);

    // Suffix - C2Data-<id>-Type<type>-<payload>b-<nPacketNum>of<nTotalPackets>
    snprintf(strInterest, nSize, "%sC2Data-%d-Type%d-%db-%dof%d", strPrefix, nId, nType, nPayload, nPacketNum, nTotalPackets);
}

// --------------------------------------------------------------------------------
//   interestQueueForDataList
//
//
// --------------------------------------------------------------------------------
std::vector<NDN_REQUEST> Consumer::interestQueueForDataList(std::vector<USER_DATA> lstUserData){

   int i, j, nPackets, nPacketPayload;
   bool bHasLeftover;   
   std::vector<NDN_REQUEST> lstRequests;
   NDN_REQUEST ndnRequest;
   USER_DATA   userData;

   // Create NDN interest packets for the entire data queue
   for (i = 0; i < (int) lstUserData.size(); i++){

      // fprintf(stdout, "[Consumer::interestQueueForDataList] Data %d/%d = %s\n", i+1, (int)lstUserData.size(), userDataToStr(lstUserData[i]));

      // Determine number of packets necessary to fulfill the interest
      userData     = lstUserData[i];
      nPackets     = userData.nPayload / N_MAX_PACKET_BYTES;
      if ((userData.nPayload % N_MAX_PACKET_BYTES) > 0){
         bHasLeftover = true;
         nPackets++;
      }
      else{
         bHasLeftover = false;
      }

      // Assemble a struct for each packet and add it to the list
      for (j = 0; j < nPackets; j++){

         if ((bHasLeftover) && (j+1 == nPackets)){
            // Last packet
            nPacketPayload = userData.nPayload % N_MAX_PACKET_BYTES;
         }
         else{
            // Any other packet
            nPacketPayload = N_MAX_PACKET_BYTES;
         }

         ndnRequest.nTimeMs = userData.nTimeMs;
         ndnRequest.bReadyToSend = false;
         getInterestFilter(ndnRequest.strInterest, sizeof(ndnRequest.strInterest), userData.strProd, userData.nId, userData.nType, nPacketPayload, j+1, nPackets);
         lstRequests.push_back(ndnRequest);
         // fprintf(stdout, "[Consumer::interestqueueForDataList] Created NDN request = %s\n", ndnRequestToStr(ndnRequest));
      }
   }
   return lstRequests;
}

// --------------------------------------------------------------------------------
//   ndnRequestToStr
//
//
// --------------------------------------------------------------------------------
char* Consumer::ndnRequestToStr(NDN_REQUEST request){
   char *strRequest = (char*) malloc(100);
   snprintf(strRequest, 100, "nTimeMs=%d; bReady=%d; interest=%s", request.nTimeMs, request.bReadyToSend, request.strInterest);
   return strRequest;
}

// --------------------------------------------------------------------------------
//   userDataToStr
//
//
// --------------------------------------------------------------------------------
char* Consumer::userDataToStr(USER_DATA userData){
   char *strData = (char*) malloc(100);
   snprintf(strData, 100, "nTimeMs=%d; nType=%d; nId=%d; nPayload=%d; prod=%s; cons=%s", userData.nTimeMs, userData.nType, userData.nId, userData.nPayload, userData.strProd, userData.strCons);
   return strData;
}

// --------------------------------------------------------------------------------
//   printNdnRequest
//
//
// --------------------------------------------------------------------------------
void Consumer::printNdnRequest(NDN_REQUEST request){
   fprintf(stdout, "[Consumer::printNdnRequest] nTimeMs=%d; bReady=%d; interest=%s\n", request.nTimeMs, request.bReadyToSend, request.strInterest);
}

// --------------------------------------------------------------------------------
//   printUserData
//
//
// --------------------------------------------------------------------------------
void Consumer::printUserData(USER_DATA userData){
   fprintf(stdout, "[Consumer::printUserData] nTimeMs=%d; nType=%d; nId=%d; nPayload=%d; prod=%s; cons=%s\n", userData.nTimeMs, userData.nType, userData.nId, userData.nPayload, userData.strProd, userData.strCons);
}

// --------------------------------------------------------------------------------
//   delayedInterest
//
//
// --------------------------------------------------------------------------------
void Consumer::delayedInterest(USER_DATA dataBuff){

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
std::vector<USER_DATA> Consumer::readDataQueue(std::string strHostName, std::string strFilePath)
{
    FILE* pFile;
    std::vector<USER_DATA> lstData;
    USER_DATA dataBuff;
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

// --------------------------------------------------------------------------------
//   logResult
//
//
// --------------------------------------------------------------------------------
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
      fprintf(stdout, "[Producer::log] ERROR opening output file at %s\n", m_strLogPath.c_str());
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
