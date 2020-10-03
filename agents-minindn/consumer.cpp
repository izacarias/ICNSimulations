/*
*    Based on Vanilla consumer for MiniNDN
*
*
*/
#include <ndn-cxx/face.hpp>
#include <iostream>
#include <chrono>
#include <ctime>
#include <libgen.h>

// Enclosing code in ndn simplifies coding (can also use `using namespace ndn`)
namespace ndn {
// Additional nested namespaces should be used to prevent/limit name conflicts
namespace examples {

class Consumer
{
   public:
      void run(std::string strInterest, std::string strNode, int nSeqNum);

   private:
      void onData(const Interest&, const Data& data)       const;
      void onNack(const Interest&, const lp::Nack& nack)   const;
      void onTimeout(const Interest& interest)             const;
      void logResult(float sTimeDiff, const char* pResult) const;
      void renameExistingLogFile();

   private:
      Face m_face;
      std::string m_strNode;
      std::string m_strInterest;
      std::string m_strLogPath;
      std::chrono::steady_clock::time_point m_dtBegin;
      int m_nSeqNum;
};

// --------------------------------------------------------------------------------
//   run
//
//
// --------------------------------------------------------------------------------
void Consumer::run(std::string strInterest, std::string strNode, int nSeqNum)
{
   Name        interestName;
   Interest    interest;
   std::chrono::steady_clock::time_point dtEnd, dtBegin;
   // time_t      dtNow;
   // struct tm*  pTimeInfo;

   if (strInterest.length() == 0){
      // No specific interest given as parameter
      strInterest = "/example/testApp/randomDataAndre";
   }

   m_strNode     = strNode;
   m_strInterest = strInterest;
   m_nSeqNum     = nSeqNum; 

   // Get current time for log file
   // time(&dtNow);
   // pTimeInfo = localtime(&dtNow);
   // strNow = ctime(&dtNow);
   // strftime (buffer, 80 ,"Now it's %I:%M%p.",timeinfo);
   // m_strLogPath  = "/tmp/minindn/" + m_strNode + "/consumerLog" + ctime(&ctime) + ".log";
   m_strLogPath  = "/tmp/minindn/" + m_strNode + "/consumerLog.log";

   std::cout << "[Consumer::run] Consuming interest=" << m_strInterest << "; node=" << m_strNode << std::endl;

   interestName = Name(m_strInterest);
   // interestName.appendVersion();

   interest = Interest(interestName);
   interest.setCanBePrefix(false);
   interest.setMustBeFresh(true);
   interest.setInterestLifetime(6_s); // The default is 4 seconds

   // dtBegin   = std::chrono::steady_clock::now();
   m_dtBegin = std::chrono::steady_clock::now();
   m_face.expressInterest(interest, bind(&Consumer::onData, this,   _1, _2),
      bind(&Consumer::onNack, this, _1, _2), bind(&Consumer::onTimeout, this, _1));

   std::cout << "[Consumer::run] Sending Interest=" << interest << std::endl;
   // processEvents will block until the requested data is received or a timeout occurs
   m_face.processEvents();

   std::cout << "[Consumer::run] Done" << std::endl;
}

// --------------------------------------------------------------------------------
//   onData
//
//
// --------------------------------------------------------------------------------
void Consumer::onData(const Interest&, const Data& data) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;
   
   // Get current time and calculate difference
   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

   logResult(sTimeDiff, "DATA");

   std::cout << "[Consumer::onData] Received Data=" << data << "Delay=" << sTimeDiff << std::endl;
}

// --------------------------------------------------------------------------------
//   onNack
//
//
// --------------------------------------------------------------------------------
void Consumer::onNack(const Interest&, const lp::Nack& nack) const
{
   float sTimeDiff;
   std::chrono::steady_clock::time_point dtEnd;

   dtEnd     = std::chrono::steady_clock::now();
   sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

   logResult(sTimeDiff, "NACK");

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

   logResult(sTimeDiff, "TIMEOUT");

   std::cout << "[Consumer::onTimeout] Timeout for interest=" << m_strInterest << "Delay="
      << sTimeDiff << std::endl;
}

// --------------------------------------------------------------------------------
//   logResult
//
//
// --------------------------------------------------------------------------------
void Consumer::logResult(float sTimeDiff, const char* pResult) const
{
   FILE* pFile;

   if (m_strNode.length() > 0){
      // Write results to file
      pFile = fopen(m_strLogPath.c_str(), "a");

      if (pFile){
         fprintf(pFile, "%s;%.4f;%s\n", m_strInterest.c_str(), sTimeDiff, pResult);
         fclose(pFile);
      }
      else{
         std::cout << "[Consumer::log] ERROR opening output file for pResult=" << pResult
             << std::endl;
      }
   }
}

// --------------------------------------------------------------------------------
//   renameExistingLogFile
//
//
// --------------------------------------------------------------------------------
void Consumer::renameExistingLogFile(){

   FILE* pFile;
   time_t rawtime;
   struct tm * pTimeInfo;
   bool bFileExists;
   char strDate[60], strNewName[60], strOldName[60];

   // Check if a previous log file should be moved
   pFile = fopen(m_strLogPath.c_str(), "r");
   bFileExists = (pFile != NULL);

   if(bFileExists){
      // Generate new filename based on time
      printf("FILE EXISTS\n");
      ctime(&rawtime);
      pTimeInfo = localtime(&rawtime);
      strcpy(strOldName, m_strLogPath.c_str());
      strftime(strDate, sizeof(strDate), "%d%m%y%H%M%S", pTimeInfo);
      snprintf(strNewName, sizeof(strNewName), "%s/oldConsumerLog_%s.log", dirname(strOldName), strDate);

      // Rename existing file
      fclose(pFile);
      if (rename(m_strLogPath.c_str(), strNewName) != 0){
         // throw("Could not rename old log file at ");
         printf("Could not change rename files from %s to %s\n", m_strLogPath.c_str(), strNewName);
      }
   }
   else
      printf("FILE DOES NOT EXIST %s\n", m_strLogPath.c_str());
}

} // namespace examples
} // namespace ndn

int main(int argc, char** argv)
{
   std::string strInterest;
   std::string strNodeName;
   int nSeqNum;

   // Assign default values
   strInterest = "";
   strNodeName = "";
   nSeqNum     = -1;

   // Command line parameters
   if (argc > 1)
      strInterest = argv[1];

   if (argc > 2)
      strNodeName = argv[2];

   if (argc > 3)
      nSeqNum = atoi(argv[3]);
   
   printf("Instantiating producer Interest=%s; NodeName=%s; SeqNum=%d\n", strInterest.c_str(), strNodeName.c_str(), nSeqNum);

   try {
      ndn::examples::Consumer consumer;
      consumer.run(strInterest, strNodeName, nSeqNum);
      return 0;
   }
   catch (const std::exception& e) {
      std::cerr << "[main] ERROR: " << e.what() << std::endl;
      return 1;
   }
}
