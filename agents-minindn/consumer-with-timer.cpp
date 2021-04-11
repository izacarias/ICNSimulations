/*
*   Vanilla consumer-with-timer for MiniNDN
*
*
*/

#include <ndn-cxx/face.hpp>
#include <ndn-cxx/util/scheduler.hpp>
#include <chrono>
#include <ctime>
#include <libgen.h>
#include <thread>

#include <boost/asio/io_service.hpp>
#include <iostream>

// Enclosing code in ndn simplifies coding (can also use `using namespace ndn`)
namespace ndn {
// Additional nested namespaces should be used to prevent/limit name conflicts
namespace examples {

class ConsumerWithTimer
{
public:
  ConsumerWithTimer()
    : m_face(m_ioService) // Create face with io_service object
    , m_scheduler(m_ioService)
  {
  }

  void
  run(std::string strHostName)
  {
    int i;
    
    m_strHostName = strHostName;
    m_strTimestamp = "";
    m_nCount = 0;

    if (m_strHostName.length() > 0)
      m_strLogPath = "/tmp/minindn/" + m_strHostName + "/consumer.log";
    else
      m_strLogPath = "/tmp/minindn/default_consumer.log";

    // Name interestName("/example/testApp/randomData");
    // interestName.appendVersion();

    // Interest interest(interestName);
    // interest.setCanBePrefix(false);
    // interest.setMustBeFresh(true);
    // interest.setInterestLifetime(2_s);

    // std::cout << "Sending Interest " << interest << std::endl;
    // m_face.expressInterest(interest,
    //                        bind(&ConsumerWithTimer::onData, this, _1, _2),
    //                        bind(&ConsumerWithTimer::onNack, this, _1, _2),
    //                        bind(&ConsumerWithTimer::onTimeout, this, _1));

    
    // Schedule a new event
  
    m_scheduler.schedule(1_s, [this] { delayedInterest(); });
    m_scheduler.schedule(2_s, [this] { delayedInterest(); });
    m_scheduler.schedule(3_s, [this] { delayedInterest(); });
    m_scheduler.schedule(4_s, [this] { delayedInterest(); });
    m_scheduler.schedule(5_s, [this] { delayedInterest(); });
    m_scheduler.schedule(6_s, [this] { delayedInterest(); });
    m_scheduler.schedule(7_s, [this] { delayedInterest(); });
    m_scheduler.schedule(8_s, [this] { delayedInterest(); });
    m_scheduler.schedule(9_s, [this] { delayedInterest(); });
    m_scheduler.schedule(10_s, [this] { delayedInterest(); });
    m_scheduler.schedule(11_s, [this] { delayedInterest(); });
    m_scheduler.schedule(12_s, [this] { delayedInterest(); });
    m_scheduler.schedule(13_s, [this] { delayedInterest(); });
    m_scheduler.schedule(14_s, [this] { delayedInterest(); });
    m_scheduler.schedule(15_s, [this] { delayedInterest(); });
    m_scheduler.schedule(16_s, [this] { delayedInterest(); });
    m_scheduler.schedule(17_s, [this] { delayedInterest(); });
    m_scheduler.schedule(18_s, [this] { delayedInterest(); });
    m_scheduler.schedule(19_s, [this] { delayedInterest(); });
    m_scheduler.schedule(20_s, [this] { delayedInterest(); });
    m_scheduler.schedule(21_s, [this] { delayedInterest(); });
    m_scheduler.schedule(22_s, [this] { delayedInterest(); });
    m_scheduler.schedule(23_s, [this] { delayedInterest(); });
    m_scheduler.schedule(24_s, [this] { delayedInterest(); });
    m_scheduler.schedule(25_s, [this] { delayedInterest(); });
    m_scheduler.schedule(26_s, [this] { delayedInterest(); });
    m_scheduler.schedule(27_s, [this] { delayedInterest(); });
    m_scheduler.schedule(28_s, [this] { delayedInterest(); });
    m_scheduler.schedule(29_s, [this] { delayedInterest(); });
    m_scheduler.schedule(30_s, [this] { delayedInterest(); });
    m_scheduler.schedule(31_s, [this] { delayedInterest(); });
    m_scheduler.schedule(32_s, [this] { delayedInterest(); });
    m_scheduler.schedule(33_s, [this] { delayedInterest(); });
    m_scheduler.schedule(34_s, [this] { delayedInterest(); });
    m_scheduler.schedule(35_s, [this] { delayedInterest(); });
    m_scheduler.schedule(36_s, [this] { delayedInterest(); });
    m_scheduler.schedule(37_s, [this] { delayedInterest(); });
    m_scheduler.schedule(38_s, [this] { delayedInterest(); });
    m_scheduler.schedule(39_s, [this] { delayedInterest(); });
    m_scheduler.schedule(40_s, [this] { delayedInterest(); });    

    // m_ioService.run() will block until all events finished or m_ioService.stop() is called
    m_ioService.run();

    // Alternatively, m_face.processEvents() can also be called.
    // processEvents will block until the requested data received or timeout occurs.
    // m_face.processEvents();
  }

private:
  void
  onData(const Interest& interest, const Data& data) const
  {
    float sTimeDiff;
    std::chrono::steady_clock::time_point dtEnd;

    dtEnd     = std::chrono::steady_clock::now();
    sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

    // logResult(sTimeDiff, "DATA", m_strTimestamp);
    logResultWithSize(sTimeDiff, "DATA", interest.getName().toUri(), m_strTimestamp, data.getContent().value_size());

    std::cout << "[Consumer::onData] Received Data=\n" << data << "Delay=" << sTimeDiff << "; Size=" << data.getContent().value_size() << std::endl;
  }

  void
  onNack(const Interest& interest, const lp::Nack& nack) const
  {
    float sTimeDiff;
    std::chrono::steady_clock::time_point dtEnd;

    dtEnd     = std::chrono::steady_clock::now();
    sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

    logResult(sTimeDiff, "NACK", interest.getName().toUri(), m_strTimestamp);
  }

  void
  onTimeout(const Interest& interest) const
  {
    float sTimeDiff;
    std::chrono::steady_clock::time_point dtEnd;

    std::cout << "[Consumer::onTimeout] Timeout for " << interest << std::endl;

    dtEnd     = std::chrono::steady_clock::now();
    sTimeDiff = std::chrono::duration_cast<std::chrono::microseconds>(dtEnd - m_dtBegin).count();

    logResult(sTimeDiff, "TIMEOUT", interest.getName().toUri(), m_strTimestamp);
  }

  void
  delayedInterest()
  {
    std::vector<const char*> lstHosts;
    std::cout << "One more Interest, delayed by the scheduler" << std::endl;
    char strBuf[100];
    int nIndex;

    lstHosts.push_back("h0");
    lstHosts.push_back("h1");
    lstHosts.push_back("h2");
    lstHosts.push_back("h3");
    lstHosts.push_back("d0");
    lstHosts.push_back("d1");
    lstHosts.push_back("d2");
    lstHosts.push_back("v0");
    lstHosts.push_back("v1");

    nIndex = rand() % lstHosts.size();
    m_nCount++;
    snprintf(strBuf, sizeof(strBuf), "/%s/TestData/%d", lstHosts[nIndex], m_nCount);

    Name interestName(strBuf);

    Interest interest(interestName);
    interest.setCanBePrefix(false);
    interest.setMustBeFresh(true);
    interest.setInterestLifetime(6_s);

    std::cout << "Sending Interest " << interest << std::endl;
    m_dtBegin = std::chrono::steady_clock::now();
    m_face.expressInterest(interest,
                           bind(&ConsumerWithTimer::onData, this, _1, _2),
                           bind(&ConsumerWithTimer::onNack, this, _1, _2),
                           bind(&ConsumerWithTimer::onTimeout, this, _1));
  }

  // --------------------------------------------------------------------------------
  //   logResult
  //
  //
  // --------------------------------------------------------------------------------
  void logResult(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp) const
  {
    FILE* pFile;

    if (m_strLogPath.length() > 0){
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
  void logResultWithSize(float sTimeDiff, const char* pResult, std::string strInterest, std::string strTimestamp, size_t nSize) const
  {
    FILE* pFile;

    if (m_strLogPath.length() > 0){
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

  

private:
  // Explicitly create io_service object, which will be shared between Face and Scheduler
  boost::asio::io_service m_ioService;
  Face m_face;
  Scheduler m_scheduler;
  std::string m_strLogPath;
  std::string m_strHostName;
  std::string m_strTimestamp;
  std::chrono::steady_clock::time_point m_dtBegin;
  int m_nCount;
};


} // namespace examples
} // namespace ndn

int
main(int argc, char** argv)
{

  std::string strNodeName;

  // Assign default values
  strNodeName  = "";
  
  // Parameter [2] host name
  if (argc > 1)
    strNodeName = argv[1];
 

  try {
    ndn::examples::ConsumerWithTimer consumer;
    consumer.run(strNodeName);
    return 0;
  }
  catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 1;
  }
}
