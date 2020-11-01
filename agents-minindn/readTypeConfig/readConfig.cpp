#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <string.h>

#define STR_CONFIGFILE_PATH "/home/andre/Source/icnsimulations/agents-minindn/readTypeConfig/c2_types.conf"
#define STR_VALID_LINE_START "Type"
#define N_DEFAULT_PAYLOAD 10
#define N_DEFAULT_TTL      5

int readTypesConfig(const char* pConfigPath, std::vector<int>* vecTTLs, std::vector<int>* vecPayloads);

int main(){

    std::vector<int> vecTTLs, vecPayloads;
    int nTypes, i;

    nTypes = readTypesConfig(STR_CONFIGFILE_PATH, &vecTTLs, &vecPayloads);

    printf("main: Read config types=%d, TTLsize=%ld, PayloadSize=%ld\n", nTypes, vecTTLs.size(), vecPayloads.size());

    // Print config read

    if (vecTTLs.size() == vecPayloads.size()){
        for (i = 0; i < vecTTLs.size(); i++){
            printf("Type %d, TTL %d, Payload %d\n", i+1, vecTTLs[i], vecPayloads[i]);
        }
    }
    else{
        printf("Sizes are not the same\n");
    }

    return nTypes;
}

int readTypesConfig(const char* pConfigPath, std::vector<int>* vecTTLs, std::vector<int>* vecPayloads){

    FILE *pConfigFile = NULL;
    char *pLine = NULL;
    size_t nLength;
    int nRead, nType, nTTL, nPayload, nReadTypes, nExpectedType;

    printf("[readTypesConfig] Reading types config from %s\n", pConfigPath);

    nReadTypes = 0;
    nExpectedType = 1;  // Types start at value 1 (not 0)
    vecTTLs->clear();
    vecPayloads->clear();
    pConfigFile = fopen(pConfigPath, "r");

    if (pConfigFile){

        // Read lines from file
        while(getline(&pLine, &nLength, pConfigFile) != -1){

            nRead = sscanf(pLine, "Type %d, TTL %d, Payload %d", &nType, &nTTL, &nPayload);

            if (nRead >= 3){
                // Valid line
                printf("[readTypesConfig] Read valid line, type=%d, TTL=%d, Payload=%d\n", nType, nTTL, nPayload);

                while((nType > 0) && (nType > nExpectedType)){
                    // Fill in type values that were skipped in config
                    vecPayloads->push_back(N_DEFAULT_PAYLOAD);
                    vecTTLs->push_back(N_DEFAULT_TTL);
                    nExpectedType++;
                }

                if (nType == nExpectedType){
                    // Type was in the expected order
                    vecTTLs->push_back(nTTL);
                    vecPayloads->push_back(nPayload);
                    nExpectedType++;
                    nReadTypes++;
                }
            }
        }
        fclose(pConfigFile);
    }
    else{
        printf("File %s not found", pConfigPath);
    }

    return nReadTypes;
}
