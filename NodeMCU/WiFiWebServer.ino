#include <Servo.h>

#include <aJSON.h>



#include <ESP8266WiFi.h>

const char* ssid = "Vikram Stud";
const char* password = "firebird";
const char* host = "192.168.10.1";
const int port = 8888;

// Create an instance of the server
// specify the port to listen on as an argument
WiFiServer server(8888);

int level[7][15];
int cell[17][15];
int check[7][2];

Servo panservo;
Servo tiltservo;


WiFiClient client;

int numRows;
String tosend;
aJsonObject *root;
void setup() {
  Serial.begin(115200);
  delay(10);

  panservo.attach(D0);
  tiltservo.attach(D1);
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print(ssid);
  Serial.println("is now online");
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  
  
  Serial.println("");
  Serial.println("WiFi connected");
  
  // Start the server
  server.begin();
  Serial.println("Server started");

  // Print the IP address
  Serial.println(myIP);
  
  

  do {
  
    client = server.available();
 
  } while(!client);

  Serial.println("new client");
  
  while(!client.available()){
    delay(1);
  }

  int a, b, start, bstart, c, d, e;
  String buff, num, digit, check;
  String arr = client.readStringUntil('\r');
  //client.flush();
  delay(1);
  //client.println("Path Read");
  
  check = client.readStringUntil('\r');
  client.flush();
  delay(1);
  client.println("Checkpoints read");
  Serial.println(arr);
  Serial.println(check);
  client.stop();
  Serial.println("Client Disconnected");
  convert(arr);
  convert_check(check);
  Serial.println();
  Serial.println();
  Serial.print("Connecting to Pi");
  
  WiFi.mode(WIFI_STA);
  delay(3000);
  WiFi.begin("RPi-4080", "firebird");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  delay(5000);
  

  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
  }

  
  root=aJson.createObject();
  
  }


void loop() {
  String a, b, c;
  
// This will send the request to the server
  aJson.addNumberToObject(root, "check", 0);
  aJson.addNumberToObject(root, "move", 1);
  tosend = aJson.print(root);
  client.print(tosend);
  delay(5000);
  Serial.println("Delaying");
////////////////////////////////////////////
  int i, j, k, pan, tilt, t, diff;
  k=0;
  t=0;
  char line[100];
  String readLine;
  Serial.println("Starting Looping");
  for (i=0; i<numRows; i++) {
    Serial.println(length_servo(level[i]));
    Serial.println();
     Serial.println();
     Serial.println();
     int l = length_servo(level[i]) - 1;
    for (j=0; j< l; j++) {
      Serial.print(j);
      Serial.print("  index   ");
      Serial.println(l);
      pan = level[i][j];
      tilt = cell[i][j];
      
      Serial.println("Reached");
       
        /*if (diff > 700) {
          aJson.addNumberToObject(root, "move", 0);
          client.print(aJson.print(root));
          
          }*/
          Serial.println("Reached1");
      if (j == l -2 && i != numRows -1) {
        level[i][j+1] = check[k][0];
        cell[i][j+1] = check[k][1];

        level[i+1][0] = check[k][0];
        cell[i+1][0] = check[k][1];
        k++;
        }
        Serial.println("Reached2");
      while ((j != l -1)) {
        if (pan == 180) {
          if (level[i][j+1] - pan > 0) {
            t = 1;
            Serial.println("switching 1");
            panservo.writeMicroseconds(1500 + ((pan - 180)- 90)*10);
            Serial.print(pan);
            Serial.print("        ");
            Serial.println(tilt);
            tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
          } else if (level[i][j+1] - pan < 0) {
            t = 0;
            Serial.println("switching 2");
            panservo.writeMicroseconds(1500 + ((pan)- 90)*10);
            Serial.print(pan);
            Serial.print("        ");
            Serial.println(tilt);
            tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
            }
          } else if (pan == 0) {
         if (level[i][j+1] - pan > 300) {
            t = 1;
            Serial.println("switching 3");
            panservo.writeMicroseconds(1500 + ((180 - pan)- 90)*10);
            Serial.print(pan);
            Serial.print("        ");
            Serial.println(tilt);
            tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
          } else if (level[i][j+1] - pan < 300) {
            t = 0;
            Serial.println("switching 4");
            panservo.writeMicroseconds(1500 + ((pan)- 90)*10);
            Serial.print(pan);
            Serial.print("        ");
            Serial.println(tilt);
            if (!(i == 0 and j== 0)) {
              tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
            }
            }
          
          }
        /*else {
          Serial.print("pan  normal");
          Serial.print(pan);
          Serial.print("        ");
          Serial.println(tilt);
            panservo.writeMicroseconds(pan);
        
        //Serial.println(pan);
        tiltservo.writeMicroseconds(tilt);
                    
          }*/
        
        //Serial.println(tilt);
      if (!(pan == level[i][j+1])) {
      
        Serial.println("Reached3");
        if (level[i][j+1] - pan > 300) {
          if (pan == 0) {
            pan = 360;
          }
          move_servo(pan, pan-1, panservo, 0);
          pan--;
            Serial.print("1   ");
            Serial.println(pan);
            //panservo.writeMicroseconds((pan-90)*10 + 1500);
          delay(3);
        } else if (level[i][j+1] - pan < -300) {
          if (pan == 360) {
              pan = 0;
            }
            move_servo(pan - 180, pan - 180 +1, panservo, 0);
          pan++;
          //panservo.writeMicroseconds(((pan - 180) - 90)*10 + 1500);
          Serial.print("2   ");
            Serial.println(pan);
          delay(3);
         } else {
       
        if (pan< level[i][j+1]) {
          
          /*Serial.print(pan);
          Serial.print(" pan ");
          Serial.println(level[i][j+1]);*/
          if (t == 1) {
            move_servo(pan - 180 , pan - 180 +1, panservo, 0);
            //panservo.writeMicroseconds(((pan - 180) - 90)*10 + 1500);
            } else {
            move_servo(pan, pan+1, panservo, 0);
            //  panservo.writeMicroseconds((pan-90)*10 + 1500);
              }
              Serial.print("3   ");
            Serial.println(pan);
              
              pan++;
          delay(3);
        }
        else if (pan > level[i][j+1]) {
          
          /*Serial.print(pan);
          Serial.print(" pan ");
          Serial.println(level[i][j+1]);*/
           if (t == 1) {
            move_servo(pan - 180, pan - 180 -1, panservo, 0);
            //panservo.writeMicroseconds(((pan - 180) - 90)*10 + 1500);
            } else {
              move_servo(pan, pan-1, panservo, 0);
              //panservo.writeMicroseconds((pan-90)*10 + 1500);
              }
              Serial.print("4   ");
            Serial.println(pan);
              pan--;
          delay(3);
        }

         }
      } 
        Serial.println("Reached4");
      if (!(tilt == cell[i][j+1])) {
        
       
        
        if (tilt < cell[i][j+1]) {
          Serial.print(tilt);
          Serial.print(" tilt ");
          Serial.println(cell[i][j+1]);
          if (t == 1) {
            move_servo( 90 - tilt, (90 - tilt) + 1, tiltservo, 1);
            //tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
            } else {
              move_servo(tilt, tilt + 1, tiltservo, 1);
              //tiltservo.writeMicroseconds((1500 + tilt*10));
              }
          delay(3);
          tilt++;
        }
        else if (tilt > cell[i][j+1]) {
          Serial.print(tilt);
          Serial.print(" tilt ");
          Serial.println(cell[i][j+1]);
          if (t == 1) {
            move_servo( 90 - tilt, (90 - tilt) - 1, tiltservo, 1);
            //tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
            } else {
            move_servo( tilt, tilt - 1, tiltservo, 1);
              //tiltservo.writeMicroseconds((1500 + tilt*10));
              }
          delay(3);
          tilt--;
        }  
          delay(3);
          
          }  else {
            Serial.print(tilt);
          Serial.print(" tilt ");
          Serial.println(cell[i][j+1]);
          if (t == 1) {
            move_servo( 90 - tilt, (90 - tilt) , tiltservo, 1);
            //tiltservo.writeMicroseconds(1500 - (1500 + tilt*10) + 1500);
            } else {
            move_servo( tilt, tilt , tiltservo, 1);
              //tiltservo.writeMicroseconds((1500 + tilt*10));
              } 
        
        } 
/*
  Serial.println("Reached 5");
  aJson.addNumberToObject(root, "move", 1);
  aJson.addNumberToObject(root, "check", 0);
  tosend = aJson.print(root);
  while(client.available()) {
    readLine = client.readStringUntil('\r');
    Serial.print(readLine);
  }  */
     if ((pan == level[i][j+1]) and (tilt == cell[i][j+1])) {
            break;
          }
  
  }
  delay(1000);
  Serial.println("Reached 6");
/*
  int x = readLine.indexOf(':', 1);
  a = readLine.substring(x+1, x+2);
  a.trim();
  int color = a.toInt();
  x = readLine.indexOf(':', x);
  b = readLine.substring(x+1, x+2);
  b.trim();
  int laser = b.toInt();

*/
     
          
    }
      delay(500);
    } // 2nd for loop
    //delay checkpoint visible
    /*Serial.println("Reaced 7");
    aJson.addNumberToObject(root, "check", 1);  
    client.print(aJson.print(root));

    while(client.available()){
    readLine = client.readStringUntil('\r');
    Serial.print(readLine);
    }

  Serial.println("Reached 8");
  int x = readLine.indexOf(':', 1);
  a = readLine.substring(x+1, x+2);
  a.trim();
  int color = a.toInt();
  x = readLine.indexOf(':', x);
  b = readLine.substring(x+1, x+2);
  b.trim();
  int laser = b.toInt();
  Serial.println("Reached 9");
    while (color != 0) {
        Serial.println("Wait for color");
      
      }
     Serial.println(color);
    //glow(color);
    delay(2000);*/
   
  
////////////////////////////////////////////
  
  
  /*unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      return;
    }
  }
  
  // Read all the lines of the reply from server and print them to Serial
  //char line[100];
  //String readLine;
  while(client.available()){
    readLine = client.readStringUntil('\r');
    Serial.print(readLine);
  }

 */

  delay(20000);
  return;
}

void move_servo(int a, int b, Servo myservo, int c) {
  int i;
  if (c == 0) {
  if (b>a) {
    a = (a - 90)*10 + 1500;
    b = (b - 90)*10 + 1500;
    for (i=a; i<=b; i++) {
        myservo.writeMicroseconds(i);
        delay(3);
      }
    } else {
      a = (a - 90)*10 + 1500;
      b = (b - 90)*10 + 1500;
      for (i=b; i<=a; i++) {
         myservo.writeMicroseconds(i);
         delay(3);
      }
      
      }
  } else {
    if (b>a) {
    a = a*10 + 1500;
    b = b*10 + 1500;
    for (i=a; i<=b; i++) {
        myservo.writeMicroseconds(i);
        delay(3);
      }
    } else {
      a = a*10 + 1500;
      b = b*10 + 1500;
      for (i=b; i<=a; i++) {
         myservo.writeMicroseconds(i);
         delay(3);
      }
    
    
    }
    
    
    
    
    }
  }


int length_servo(int arr[]) {
  int i;
  for (i=0; arr[i] != 450; i++) {
    }
  return i+1;
  }
void convert(String arr) {


  int a, b, start, bstart, c, d, e;
  String buff, num, digit;

  Serial.println(arr);

  start = 1;
  int i, j;
  i=0;
  j=0;

  Serial.println(arr);
  
  do {
    a = arr.indexOf('[', start);  
    b = arr.indexOf(']', start);
    
    buff = arr.substring(a, b+1);
    start = b+1;
    bstart = 0;
    Serial.println(buff);
    j=0;
    do {
        c = buff.indexOf('(', bstart);
        e = buff.indexOf(')', bstart);
        
        num = buff.substring(c+1, e);
        Serial.println(num);

        d = num.indexOf(',');

        digit = num.substring(0, d);
        digit.trim();
        Serial.println(digit.toInt());
        level[i][j] = digit.toInt();
        digit = num.substring(d+1);
        digit.trim();
        Serial.println(digit.toInt());
        cell[i][j] = digit.toInt();
        

        
        j++;

        bstart = e+1;
      } while(buff.indexOf('(', bstart) != -1);

      Serial.println(i);
      Serial.println(j);
      level[i][j] = 450;
      cell[i][j] = 450;
      
      
      i++;
    
    } while(arr.indexOf('[', start) != -1);

    numRows = i;
  
    for (i = 0; i < numRows; i++) {
      j=0;
      while(level[i][j] != -1) {
        
        Serial.print(level[i][j]);
        Serial.print("\t");
        Serial.println(cell[i][j]);
        j++;
        }
      
      
      }

  

}


void convert_check(String checkp) {
  int bstart = 1;
  int i = 0;
  int c, d, e;
  String num, digit;
  do {
        c = checkp.indexOf('(', bstart);
        e = checkp.indexOf(')', bstart);
        
        num = checkp.substring(c+1, e);
        Serial.println(num);

        d = num.indexOf(',');

        digit = num.substring(0, d);
        digit.trim();
        Serial.println(digit.toInt());
        check[i][0] = digit.toInt();
        digit = num.substring(d+1);
        digit.trim();
        Serial.println(digit.toInt());
        check[i][1] = digit.toInt();
        

        
        i++;

        bstart = e+1;
      } while(checkp.indexOf('(', bstart) != -1);
  
  
  
  }
