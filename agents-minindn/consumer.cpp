/*
*    Based on Vanilla consumer for MiniNDN
*
*    André Dexheimer Carneiro 02/11/2020
*   
*    Usage: consumer <interest> <hostName> <payload> <timestamp>
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

#define N_DEFAULT_PAYLOAD_BYTES 100
#define N_MAX_PACKET_BYTES      8000

// Enclosing code in ndn simplifies coding (can also use `using namespace ndn`)
namespace ndn {
// Additional nested namespaces should be used to prevent/limit name conflicts
namespace examples {

class Consumer
{
   public:
      void run(std::string strInterest, std::string strNode, std::string strTimestamp, int nPayload);

   private:
      void onData(const Interest&, const Data& data)       const;
      void onNack(const Interest&, const lp::Nack& nack)   const;
      void onTimeout(const Interest& interest)             const;
      void logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp) const;
      void logResultWithSize(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const;
      void consumePacket(std::string strInterest);

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
void Consumer::run(std::string strInterest, std::string strNode, std::string strTimestamp, int nPayload)
{
   Name     interestName;
   Interest interest;
   std::string strPacketInterest;
   int nPackets, nPacketPayload, i;
   std::vector<std::thread> lstThreads;
   std::thread threadBuffer;
   char strBuf[200];
   bool bHasLeftover=false;

   ////////////////////////////////////////////////
   // Read and validate input parameters
   m_strHostName  = strNode;
   m_strTimestamp = strTimestamp;

   if (strInterest.length() > 0)
      m_strInterest = strInterest;
   else
      m_strInterest = "/example/testApp/randomDataAndre";

   if (m_strHostName.length() > 0)
      m_strLogPath = "/tmp/minindn/" + m_strHostName + "/consumerLog.log";
   else
      m_strLogPath = "/tmp/minindn/default_consumerLog.log";

   fprintf(stdout, "[Consumer::run] Running consumer with Interest=%s; HostName=%s; Timestamp=%s\n", m_strInterest.c_str(), m_strHostName.c_str(), m_strTimestamp.c_str());

   ///////////////////////////////////////////////
   // Determine number of packets based on data type
   nPackets = nPayload / N_MAX_PACKET_BYTES;
   if ((nPayload % N_MAX_PACKET_BYTES) > 0){
      bHasLeftover = true;
      nPackets++;
   }

   fprintf(stdout, "[Consumer::run] About to instantiate %d threads for a total of %d bytes\n", nPackets, nPayload);

   ///////////////////////////////////////////////
   // Launch a thread for each packet
   for (i = 0; i < nPackets; i++){

      if ((i+1 == nPackets) && (bHasLeftover)){
         // Last packet
         nPacketPayload = nPayload % N_MAX_PACKET_BYTES;
      }
      else{
         // Any other packet
         nPacketPayload = N_MAX_PACKET_BYTES;
      }

      /////////////////////////////////////////////////
      // Get start time before expressInterest, end time will be captured by onData/onNack/onTimeout callback
      m_dtBegin = std::chrono::steady_clock::now();
         
      snprintf(strBuf, sizeof(strBuf), "%s-%db-%dof%d", m_strInterest.c_str(), nPacketPayload, i+1, nPackets);
      strPacketInterest = strBuf;
      fprintf(stdout, "[Consumer::run] Starting thread %d/%d for interest=%s\n", i+1, nPackets, strPacketInterest.c_str());
      lstThreads.push_back(std::thread(&Consumer::consumePacket, this, strPacketInterest));
   }

   fprintf(stdout, "[Consumer::run] Waiting for %d threads on interest=%s\n", nPackets, m_strInterest.c_str());
   for (i = 0; i < (int) lstThreads.size(); i++){
      lstThreads[i].join();
   }

   // m_face.expressInterest(interest, bind(&Consumer::onData, this,   _1, _2),
   //    bind(&Consumer::onNack, this, _1, _2), bind(&Consumer::onTimeout, this, _1));

   // // pocessEvents will block until the requested data is received or a timeout occurs
   // m_face.processEvents();

   fprintf(stdout, "[Consumer::run] Done\n");
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
   
   int nPayload;
   std::string strInterest;
   std::string strNodeName;
   std::string strTimestamp;

   // Assign default values
   strInterest  = "";
   strNodeName  = "";
   strTimestamp = "0";
   nPayload     = N_DEFAULT_PAYLOAD_BYTES;  

   // Command line parameters
   // Usage: consumer <interest> <hostName> <payload> <timestamp>
   // Parameter [1] interest filter
   if (argc > 1)
      strInterest = argv[1];
   // Parameter [2] host name
   if (argc > 2)
      strNodeName = argv[2];
   // Parameter [3] payload
   if (argc > 3)
      nPayload = atoi(argv[3]);
   // Parameter [4] timestamp of start time
   if (argc > 4)
      strTimestamp = argv[4];

   try {
      ndn::examples::Consumer consumer;
      consumer.run(strInterest, strNodeName, strTimestamp, nPayload);
      return 0;
   }
   catch (const std::exception& e) {
      std::cerr << "[main] ERROR: " << e.what() << std::endl;
      return 1;
   }
}
