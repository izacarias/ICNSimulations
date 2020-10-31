#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <string.h>

#define STR_CONFIGFILE_PATH "/home/andre/Source/icnsimulations/agents-minindn/readTypeConfig/c2_types.conf"
#define STR_VALID_LINE_START "Type"

int readTypesConfig(const char* pConfigPath);

int main(){

    int nResult;
    // std::vector<int> vecTTL;
    // std::vector<int> vecPayload;
    nResult = readTypesConfig(STR_CONFIGFILE_PATH);

    return 0;
}

int readTypesConfig(const char* pConfigPath){

    FILE *pConfigFile;
    char *pLine;
    size_t nLength;
    int nRead, nType, nTTL, nPayload, nTypes;

    nTypes = 0;

    pConfigFile = fopen(pConfigPath, "r");

    if (pConfigFile){

        // Read lines from file
        while(getline(&pLine, &nLength, pConfigFile) != -1){

            nRead = sscanf(pLine, "Type %d, TTL %d, Payload %d", &nType, &nTTL, &nPayload);

            if (nRead >= 3){
                // Valid line
                printf("Read valid line, type=%d, TTL=%d, Payload=%d\n", nType, nTTL, nPayload);
            }
            else{
                // Invalid (ignored) line
                printf("Read ignored line: %s", pLine);
            }
        }
        fclose(pConfigFile);
    }
    else{
        printf("File %s not found", pConfigPath);
    }

    return nTypes;
}
