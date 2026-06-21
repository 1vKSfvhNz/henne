#include "ethercat_master.hpp"
#include <ethercat.h>

class EtherCATMaster {
private:
    int sock;  // Socket EtherCAT
    std::vector<Slave> slaves;
    
public:
    bool initialize() {
        // Initialiser la communication EtherCAT
        sock = ec_open_socket();
        if (sock < 0) {
            return false;
        }
        
        // Configurer les esclaves
        ec_config_init();
        
        // Détecter les esclaves
        int slave_count = ec_slavecount();
        if (slave_count < 3) {
            return false; // Pas assez d'esclaves
        }
        
        return true;
    }
    
    void send_motor_commands(float x, float y, float z) {
        // Envoyer les positions aux moteurs
        uint8_t* pdo = ec_slave[1].outputs;
        memcpy(pdo, &x, 4);
        memcpy(pdo + 4, &y, 4);
        memcpy(pdo + 8, &z, 4);
        
        // Mise à jour du bus
        ec_send();
        ec_receive();
    }
    
    void set_piezo_frequency(uint8_t nozzle, float frequency) {
        // Configurer la tête piézo
        uint8_t* pdo = ec_slave[2].outputs;
        pdo[nozzle * 2] = (uint8_t)(frequency * 10); // 10kHz max
    }
};