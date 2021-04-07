/*
*   Based on vanilla producer for MiniNDN
*
*   André Dexheimer Carneiro 02/11/2020
*/

#include <ndn-cxx/face.hpp>
#include <ndn-cxx/security/key-chain.hpp>
#include <ndn-cxx/security/signing-helpers.hpp>
#include <libgen.h>
#include <iostream>
#include <string.h>
#include <boost/chrono/duration.hpp>
#include <ndn-cxx/util/random.hpp>

#define STR_APPNAME             "C2Data"
#define N_DEFAULT_TTL_MS        10000

int g_nDefaultPayload = 100;

// Enclosing code in ndn simplifies coding (can also use `using namespace ndn`)
namespace ndn {
// Additional nested namespaces should be used to prevent/limit name conflicts
namespace examples {

static std::string getRandomByteString(std::size_t length);

class Producer
{
  public:
    void run(std::string strFilter, std::vector<int> lstTTLs);

  private:
    void onInterest(const InterestFilter&, const Interest& interest);
    void onRegisterFailed(const Name& prefix, const std::string& reason);
    void printTypesConfig();
  
    int getTTLMsFromType(int nType);

  private:
    Face           m_face;
    KeyChain       m_keyChain;
    std::vector<int> m_lstTTLs;
};

// --------------------------------------------------------------------------------
//  run
//
//
// --------------------------------------------------------------------------------
void Producer::run(std::string strFilter, std::vector<int> lstTTLs)
{
  fprintf(stderr, "[Producer::run] Begin\n");

  if (strFilter.length() == 0){
    // No specific filter set
    strFilter = "/exampleApp/blup";
  }

  m_lstTTLs = lstTTLs;

  fprintf(stderr, "[Producer::run] Producer for filter=%s with TTLs=%ld\n", strFilter.c_str(), m_lstTTLs.size());
  printTypesConfig();

  // strInterest = '/' + c_strAppName + '/' + str(producer) + '/' + strInterest
  // nullptr is because RegisterPrefixSuccessCallback is optional
  m_face.setInterestFilter(strFilter, bind(&Producer::onInterest, this, _1, _2), nullptr, bind(&Producer::onRegisterFailed, this, _1, _2));
  m_face.processEvents();
  fprintf(stderr, "[Producer::run] End\n");
}

// --------------------------------------------------------------------------------
//  onInterest
//
//
// --------------------------------------------------------------------------------
void Producer::onInterest(const InterestFilter&, const Interest& interest)
{
  int nType, nID, nPayloadSize, nTTLMs;
  std::string strPacket;
  std::string strContent;

  strPacket    = interest.getName().toUri();
  nPayloadSize = 0;
  nType        = 0;
  nID          = -1;
  sscanf(basename((char*) strPacket.c_str()), "C2Data-%d-Type%d-%db", &nID, &nType, &nPayloadSize);
  printf("[Producer::onInterest] Interest for packet=%s\n", strPacket.c_str());

  // Determine TTL and payload
  nTTLMs = getTTLMsFromType(nType);
  if (nPayloadSize == 0)
    nPayloadSize = g_nDefaultPayload;

  printf("[Producer::onInterest] nType=%d; nID=%d; TTLms=%d; PayloadSize=%d\n", nType, nID, nTTLMs, nPayloadSize);  
  
  // This used to be how the payload was allocated
  // const char *pPayload;
  // pPayload = (char*) malloc(nPayloadSize);
  // data->setContent(reinterpret_cast<const uint8_t*>(pPayload), nPayloadSize);

  // Create packet for interest
  auto data  = make_shared<Data>(interest.getName());
  strContent = getRandomByteString(nPayloadSize);
  data->setContent(reinterpret_cast<const uint8_t*>(strContent.data()), strContent.length());
  data->setFreshnessPeriod(boost::chrono::milliseconds(nTTLMs));
  m_keyChain.sign(*data);

  /////////////////////////////////////////////////////////////////////////////
  // interest.toUri() results in the same thing
  // Format: /drone/%FD%00...AF?MustBeFresh&Nonce=43a724&Lifetime=6000
  //
  // with Sec as boost::chrono::seconds
  // data->setFreshnessPeriod(Sec);   // 60s is the default for control data
  //
  // for a static const std::string strContent
  // data->setContent(reinterpret_cast<const uint8_t*>(strContent.data()), strContent.size());
  //
  // Sign Data packet with default identity
  // m_keyChain.sign(*data, signingByIdentity(<identityName>));
  // m_keyChain.sign(*data, signingByKey(<keyName>));
  // m_keyChain.sign(*data, signingByCertificate(<certName>));
  // m_keyChain.sign(*data, signingWithSha256());
  //////////////////////////////////////////////////////////////////////////////

  // Return Data packet to the requester
  std::cout << "[Producer::onInterest] << D: " << *data << std::endl;
  m_face.put(*data);
  // free((void*) pPayload);
  std::cout << "[Producer::onInterest] End"  << std::endl;
}

// --------------------------------------------------------------------------------
//  getTTLMsFromType
//
//
// --------------------------------------------------------------------------------
int Producer::getTTLMsFromType(int nType)
{
  int nTTL = N_DEFAULT_TTL_MS;
  if ((nType > 0) && ((uint) nType <= m_lstTTLs.size())){
    // The starting value for nType is 1
    nTTL = m_lstTTLs[nType-1];
  }
  return nTTL;
}

// --------------------------------------------------------------------------------
//  printTypesConfig
//
//
// --------------------------------------------------------------------------------
void Producer::printTypesConfig()
{
  unsigned int i;
  int nTTL;
  for (i = 1; i <= m_lstTTLs.size(); i++){
    nTTL = getTTLMsFromType(i);
    printf("[Producer::printTypesConfig] Type %d - TTL %d\n", i, nTTL);
  }
}

// --------------------------------------------------------------------------------
//  onRegisterFailed
//
//
// --------------------------------------------------------------------------------
void Producer::onRegisterFailed(const Name& prefix, const std::string& reason)
{
  std::cerr << "[Producer::onRegisterFaile] ERROR: Failed to register prefix '" << prefix
            << "' with the local forwarder (" << reason << ")" << std::endl;
  m_face.shutdown();
}

// --------------------------------------------------------------------------------
//  getRandomByteString
//
//
// --------------------------------------------------------------------------------
static std::string getRandomByteString(std::size_t length)
  {
    // per ISO C++ std, cannot instantiate uniform_int_distribution with char
    static std::uniform_int_distribution<short> dist(std::numeric_limits<char>::min(),
                                                     std::numeric_limits<char>::max());

    std::string s;
    s.reserve(length);
    for (std::size_t i = 0; i < length; i++) {
      s += static_cast<char>(dist(random::getRandomNumberEngine()));
    }
    return s;
  }

} // namespace examples
} // namespace ndn

int main(int argc, char** argv)
{
  std::string      strFilter;
  std::vector<int> lstTTLs;
  unsigned int i;
  int j;
  bool bDefaultPayloadSet=false;

  fprintf(stderr, "[main] Begin");

  strFilter = "";

  // Parameter [1] interest filter
  if (argc > 1)
    strFilter = argv[1];

  // If there are only 2 paremeters (disconsidering & as last parameter), use value as default payload
  if ((argc == 3) || ((argc == 4) and (strcmp(argv[3], "&") != 0))){
    g_nDefaultPayload = atoi(argv[2]);
    bDefaultPayloadSet = true;
    fprintf(stderr, "[main] Default payload set, nDefaultPayload=%d bytes\n", g_nDefaultPayload);
  }

  if (!bDefaultPayloadSet){
    // Parameter [2..] list of TTLs and payloads
    if (argc > 2){
      for (j = 2; j < argc; j++){
        if (strcmp(argv[j], "&") != 0){
          // Ignore char used to run producer in the background
          lstTTLs.push_back(atoi(argv[j]));
        }      
      }
    }
  }

  try {
    ndn::examples::Producer producer;
    producer.run(strFilter, lstTTLs);
    fprintf(stderr, "[main] End");
    return 0;
  }
  catch (const std::exception& e) {
    std::cerr << "[main] ERROR: " << e.what() << std::endl;
    return 1;
  }
}
