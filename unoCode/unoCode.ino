int ramPin =3;
int tmpCPUPin = 5;
int cpuPin=6;
int tmpGPUPin=9;
int gpuPin=10;
int netPin=11;

int ram =0;
int tmpCPU = 0;
int cpu=0;
int tmpGPU=0;
int gpu=0;
int net=0;


void setup() {
  Serial.begin(115200);
  pinMode(ramPin, OUTPUT);
  pinMode(tmpCPUPin, OUTPUT);
  pinMode(cpuPin, OUTPUT);
  pinMode(tmpGPUPin, OUTPUT);
  pinMode(gpuPin, OUTPUT);
  pinMode(netPin, OUTPUT);

}

void loop() {
  while(Serial.available()==0){
    //wait to start
  }
  String str=Serial.readStringUntil('\r');
  if(str[0] == 's'){
    int statCount=0;
    String tmpStr = "";
    for (int i =1; i < str.length(); i++){
      if(str[i] != ':'){
        tmpStr = tmpStr + str[i];
      }
      else{
        int stat = tmpStr.toInt();
        tmpStr = "";
        switch(statCount){
          case 0:
            ram = stat;
          case 1:
            tmpCPU = stat;
          case 2:
            cpu=stat;
          case 3:
            tmpGPU=stat;
          case 4:
            gpu=stat;
          case 5:
            net = stat;
        }
        statCount++;
      }
    }
    analogWrite(ramPin, (ram*134/100));
    analogWrite(tmpCPUPin, (tmpCPU*136/100));
    analogWrite(cpuPin, (cpu*140/100));
    analogWrite(tmpGPUPin, (tmpGPU*140/100));
    analogWrite(gpuPin, (gpu*144/100));
    analogWrite(netPin, (net*142/100));
  }
  if (str=="reset"){
    analogWrite(ramPin, 0);
    analogWrite(tmpCPUPin, 0);
    analogWrite(cpuPin, 0);
    analogWrite(tmpGPUPin, 0);
    analogWrite(gpuPin, 0);
    analogWrite(netPin, 0);
  }

//  Serial.println(ram);
//  Serial.println(tmpCPU);
//  Serial.println(cpu);
//  Serial.println(tmpGPU);
//  Serial.println(gpu);
//  Serial.println(net);

}
