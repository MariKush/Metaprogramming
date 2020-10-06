importsun.security.util.BitArray;

importstaticorg.Masha.Helper. * ;

/*
    wwwwww
*/intx;
publicclassDES{

//comment
privateBitArray[]splitBlock(BitArrayE){
BitArray[]blocks = newBitArray[8];

for (inti = 0;i<8;i++){//com2
blocks[i] = newBitArray(6);
for (intj = 0;j<6;j++){
blocks[i].set(j,E.get(i * 6+j));
}
}
returnblocks;
}

privateBitArrayextendBlock(BitArrayR){
BitArrayE = newBitArray(48);
for (inti = 0;i<48;i++){
E.set(i,R.get(extensionTable[i]));
}
returnE;
}

privateBitArrayxor(BitArraya,BitArrayb){
if (a.length() != b.length())thrownewIllegalArgumentException("input has no same size");

BitArrayresult = newBitArray(b.length());
for (inti = 0;i<a.length();i++){
result.set(i,a.get(i) ^ b.get(i));
}
returnresult;
}


privateBitArrayfeistelHelper(BitArrayR,BitArraykey){
BitArrayresult = newBitArray(32);

BitArrayextendBlock = extendBlock(R);
extendBlock = xor(extendBlock,key);


BitArray[]blocks = splitBlock(extendBlock);
BitArraytempRes = newBitArray(32);
for (inti = 0;i<8;i++){
inta = toInt(blocks[i].get(0)) * 2+toInt(blocks[i].get(5));
intb = toInt(blocks[i].get(1)) * 8+toInt(blocks[i].get(2)) * 4+toInt(blocks[i].get(3)) * 2+toInt(blocks[i].get(4));
intc = blockTransformationTables[i][a][b];
for (intj = 3;j >= 0;j--){
tempRes.set(i * 4+j,(c % 2 == 1));
c = c / 2;
}

}
for (inti = 0;i<32;i++){
result.set(i,tempRes.get(replaseTableP[i]));
}
returnresult;
}


privateBitArrayfeistelEncrypt(BitArrayinput,Keykey){
BitArrayoutput = newBitArray(64),
L = newBitArray(32),
R = newBitArray(32),
temp,f;
for (inti = 0;i<32;i++){
L.set(i,input.get(i));
R.set(i,input.get(i+32));
}

for (inti = 0;i<16;i++){
BitArraysubKey = key.getKey(i);
temp = R;
f = feistelHelper(R,subKey);
R = xor(L,f);
L = temp;
}

for (inti = 0;i<32;i++){
output.set(i,L.get(i));
output.set(i+32,R.get(i));
}

returnoutput;
}

privateBitArrayreplaseS(BitArrayinput){
BitArrayoutput = newBitArray(input.length());
for (inti = 0;i<64;i++){
output.set(i,input.get(replaseTable1[i]));
}
returnoutput;
}

privateBitArrayreplaseB(BitArrayinput){
BitArrayoutput = newBitArray(input.length());
for (inti = 0;i<64;i++){
output.set(replaseTable1[i],input.get(i));
}
returnoutput;
}

publicStringencrypt(Stringinput,StringkeyS,StringinitStr){
Keykey = newKey(keyS);

while (input.length() % 8 != 0){
input = input.concat(String.valueOf('\0'));
}
Stringoutput = "";

BitArraypreviousEncryptedBlock = newBitArray(64,initStr.getBytes());

for (inti = 0;i<input.length() / 8;i++){
BitArrayarr = previousEncryptedBlock;

arr = replaseS(arr);
arr = feistelEncrypt(arr,key);
arr = replaseB(arr);

arr = xor(arr,newBitArray(64,input.substring(i * 8,(i+1) * 8).getBytes()));

output = output.concat(newString(arr.toByteArray()));

previousEncryptedBlock = arr;
}

returnoutput;
}

publicStringdecrypt(Stringinput,StringkeyS,StringinitStr){
if (input.length() % 8 != 0){
thrownewIllegalArgumentException("input has incorrect size");
}
Keykey = newKey(keyS);
Stringresult = "";

BitArraypreviousEncryptedBlock = newBitArray(64,initStr.getBytes());

for (inti = 0;i<input.length() / 8;i++){
BitArrayarr = previousEncryptedBlock;

arr = replaseS(arr);
arr = feistelEncrypt(arr,key);
arr = replaseB(arr);

BitArraycurrEncryptedBlock = newBitArray(64,input.substring((i) * 8,(i+1) * 8).getBytes());
arr = xor(currEncryptedBlock,arr);

result = result.concat(newString(arr.toByteArray()));

previousEncryptedBlock = currEncryptedBlock;
}

returnresult.replace("\0","");
}

}