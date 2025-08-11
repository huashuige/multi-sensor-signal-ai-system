#ifndef USB5000_H
#define USB5000_H

int _stdcall FindUSB5DAQ();
int _stdcall USB5OpenDevice(int DevIndex);
int _stdcall USB5CloseDevice(int DevIndex);
int _stdcall USB5GetDeviceSN(int DevIndex, char *SN);
int _stdcall USB5ReadDevcieSN(int DevIndex);
int _stdcall USB5GetDeviceModel(int DevIndex, char *Model);
int _stdcall USB5ReadDevcieModel(int DevIndex);
int _stdcall USB5ReadFpgaVersion(int DevIndex);

//--------------------------------------------------------------------------
// Ananlog Input Configuration

int _stdcall SetUSB5AiSampleRate(int DevIndex, unsigned int SamplePeriod);
int _stdcall SetUSB5AiSampleMode(int DevIndex, unsigned char AiSampleMode);
// int _stdcall SetUSB5AiConnectType(int DevIndex, unsigned char AiConnectType);
int _stdcall SetUSB5AiRange(int DevIndex, unsigned char Chan, float AiRange);
int _stdcall SetUSB5AiChanSel(int DevIndex, unsigned char Chan, unsigned char Sel);
int _stdcall SetUSB5AiTrigSource(int DevIndex, unsigned char AiTrigSource);
int _stdcall SetUSB5AiConvSource(int DevIndex, unsigned char AiConvSource);
int _stdcall SetUSB5AiPreTrigPoints(int DevIndex, unsigned int AiPreTrigPoints);
int _stdcall SetUSB5AiOneShotPoints(int DevIndex, unsigned int AiOneShotPoints);
int _stdcall SetUSB5ClrAiFifo(int DevIndex);

//--------------------------------------------------------------------------
// Digital I/O Configuration

int _stdcall SetUSB5DiSampleRate(int DevIndex, unsigned int SamplePeriod);
int _stdcall SetUSB5DiSampleMode(int DevIndex, unsigned char DiSampleMode);
int _stdcall SetUSB5DiTrigSource(int DevIndex, unsigned char DiTrigSource);
int _stdcall SetUSB5DiConvSource(int DevIndex, unsigned char DiConvSource);
int _stdcall SetUSB5DiPreTrigPoints(int DevIndex, unsigned int DiPreTrigPoints);
int _stdcall SetUSB5DiOneShotPoints(int DevIndex, unsigned int DiOneShotPoints);
int _stdcall SetUSB5ClrDiFifo(int DevIndex);

int _stdcall SetUSB5DoSampleRate(int DevIndex, unsigned int SamplePeriod);
int _stdcall SetUSB5DoSampleMode(int DevIndex, unsigned char DoSampleMode);
int _stdcall SetUSB5DoTrigSource(int DevIndex, unsigned char DoTrigSource);
int _stdcall SetUSB5DoConvSource(int DevIndex, unsigned char DoConvSource);
int _stdcall SetUSB5DoCycle(int DevIndex, unsigned int DoCycle);
int _stdcall SetUSB5DoDataFifo(int DevIndex, unsigned int Value[], unsigned int Len);
int _stdcall SetUSB5ClrDoFifo(int DevIndex);
int _stdcall SetUSB5DoWaveCtrl(int DevIndex, unsigned int Chan);
int _stdcall SetUSB5DoImmediately(int DevIndex, unsigned int Chan, unsigned int Value);

//--------------------------------------------------------------------------
// Ananlog Output Configuration

int _stdcall SetUSB5AoSampleRate(int DevIndex, unsigned char Chan, unsigned int SamplePeriod);
int _stdcall SetUSB5AoSampleMode(int DevIndex, unsigned char Chan, unsigned char AoSampleMode);
int _stdcall SetUSB5AoTrigSource(int DevIndex, unsigned char Chan, unsigned char AoTrigSource);
int _stdcall SetUSB5AoConvSource(int DevIndex, unsigned char Chan, unsigned char AoConvSource);
int _stdcall SetUSB5AoCycle(int DevIndex, unsigned char Chan, unsigned int AoCycle);
int _stdcall SetUSB5AoDataFifo(int DevIndex, unsigned char Chan, float *Voltage, unsigned int Len);
int _stdcall SetUSB5ClrAoFifo(int DevIndex, unsigned char Chan);
int _stdcall SetUSB5AoSync(int DevIndex, unsigned char Chans);
int _stdcall SetUSB5AoImmediately(int DevIndex, unsigned char Chan, float Voltage);
int _stdcall SetUSB5AoWaveKB(int DevIndex, unsigned char Chan, float k, float b);

//--------------------------------------------------------------------------
// Trig Control

int _stdcall SetUSB5AiSoftTrig(int DevIndex);
int _stdcall SetUSB5DiSoftTrig(int DevIndex);
int _stdcall SetUSB5DoSoftTrig(int DevIndex);
int _stdcall SetUSB5AoSoftTrig(int DevIndex, unsigned char Chan);
int _stdcall SetUSB5GlobalSoftTrig(int DevIndex);

int _stdcall SetUSB5ClrTrigger(int DevIndex);
int _stdcall SetUSB5ClrAiTrigger(int DevIndex);
int _stdcall SetUSB5ClrDiTrigger(int DevIndex);
int _stdcall SetUSB5ClrDoTrigger(int DevIndex);
int _stdcall SetUSB5ClrAoTrigger(int DevIndex, unsigned char Chan);
int _stdcall SetUSB5ClrGlobalSoftTrig(int DevIndex);

//--------------------------------------------------------------------------
// Sync Configuration

int _stdcall SetUSB5ExtTrigOutSource(int DevIndex,unsigned char Source);
int _stdcall SetUSB5ExtConvOutSource(int DevIndex,unsigned char Source);

//--------------------------------------------------------------------------
// Get Data Acquired

int _stdcall USB5GetAi(int DevIndex, unsigned long Points, float *Ai, long TimeOut);
int _stdcall USB5GetDi(int DevIndex, unsigned long Points, unsigned char *Di, long TimeOut);

//--------------------------------------------------------------------------
// 校准时使用的函数

int _stdcall GoToCalibrate(int DevIndex);
int _stdcall WriteFlash(int DevIndex, short Addr, unsigned char *data);
int _stdcall ReadAiKB(int DevIndex, int chan, float *KB);
int _stdcall ReadAoKB(int DevIndex, int chan, float *KB);

//--------------------------------------------------------------------------
// ERROR CODE

const int NO_USBDAQ = -1;
const int DevIndex_Overflow = -2;
const int Bad_Firmware = -3;
const int USBDAQ_Closed = -4;
const int Transfer_Data_Fail = -5;
const int NO_Enough_Memory = -6;
const int Time_Out = -7;
const int Not_Reading = -8;
const int ChanIndex_Overflow = -9;
const int Undefined_AiRange = -10;
const int Undefined_SamplePeriod = -11;
const int Undefined_AiConnectType = -12;
const int Undefined_AiSampleMode = -13;
const int Undefined_WaveLen = -14;
const int Undefined_Paramter = -15;

#endif