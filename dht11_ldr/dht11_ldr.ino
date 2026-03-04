#include <DHT11.h>

#define DHTPIN 2       
#define LDRPIN A0      

// Avec cette bibliothèque, on ne met que la PIN, pas le TYPE
DHT11 dht11(DHTPIN); 

void setup() {
  Serial.begin(9600);
  // Pas besoin de dht.begin() avec cette bibliothèque
}

void loop() {
  int temperature = 0;
  int humidite = 0;

  // Cette bibliothèque renvoie un code erreur (0 = OK)
  int resultat = dht11.readTemperatureHumidity(temperature, humidite);

  int luminosite = analogRead(LDRPIN);

  if (resultat == 0) {
    // Format JSON
    Serial.print("{\"temp\":");
    Serial.print(temperature);
    Serial.print(",\"hum\":");
    Serial.print(humidite);
    Serial.print(",\"lum\":");
    Serial.print(luminosite);
    Serial.println("}");
  } else {
    Serial.println("{\"erreur\":\"Erreur de lecture DHT11\"}");
  }

  delay(2000);
}
