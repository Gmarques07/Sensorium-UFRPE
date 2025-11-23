/*
 * Exemplo de código Arduino para envio de dados ao Sensorium
 * 
 * Este código demonstra como o seu sensor Arduino pode se comunicar com o Sistema Sensorium
 * usando a chave de API gerada na interface web.
 * 
 * Você precisará:
 * 1. Instalar as bibliotecas: WiFi, HTTPClient
 * 2. Substituir "SUA_CHAVE_API_AQUI" pela chave fornecida no dashboard
 * 3. Configurar as credenciais da sua rede Wi-Fi
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Dados de conexão Wi-Fi
const char* ssid = "NOME_DA_SUA_REDE_WIFI";
const char* password = "SENHA_DA_SUA_REDE_WIFI";

// URL do servidor Sensorium
const char* serverName = "http://SEU_SERVIDOR:8001";  // Atualize com o IP/domínio do seu servidor

// Substitua esta chave pela chave fornecida no dashboard do Sensorium
String apiKey = "SUA_CHAVE_API_AQUI";

// IDs e variáveis de exemplo
int dispositivoId = 1; // Este ID será atribuído quando você registrar o sensor

void setup() {
  Serial.begin(115200);
  
  // Conectar ao Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Conectado ao Wi-Fi!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Simular leitura de sensores
  float phValor = analogRead(A0) * (5.0 / 1023.0) * 2.0; // Simulação de leitura de pH
  int nivelAgua = analogRead(A1) > 512 ? 1 : 0; // Simulação de sensor de nível (1 = cheio, 0 = vazio)
  String statusNivel = nivelAgua ? "ALTO" : "BAIXO";
  
  // Enviar dados para o servidor Sensorium
  enviarDadosParaSensorium(phValor, nivelAgua, statusNivel);
  
  // Aguardar antes da próxima leitura
  delay(15000); // Envia a cada 15 segundos
}

void enviarDadosParaSensorium(float ph, int boia, String statusBoia) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Construir a URL
    String serverPath = String(serverName) + "/api/v1/leituras/";
    
    http.begin(serverPath);
    
    // Configurar headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + apiKey);
    
    // Criar JSON com os dados
    DynamicJsonDocument doc(1024);
    doc["ph"] = ph;
    doc["boia"] = boia;
    doc["status_boia"] = statusBoia;
    doc["dispositivo_id"] = dispositivoId;
    
    // Converter para string
    String httpRequestData;
    serializeJson(doc, httpRequestData);
    
    // Fazer a requisição POST
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Código de resposta HTTP: " + String(httpResponseCode));
      Serial.println("Resposta: " + response);
    } else {
      Serial.println("Erro na requisição HTTP: " + String(httpResponseCode));
    }
    
    // Limpar a conexão
    http.end();
  } else {
    Serial.println("Não conectado ao Wi-Fi");
  }
}