% Шакалит шакала
S=imread("jackal.png");

S2=imresize(S,[32 32]);

figure;
subplot(2,2,1);
imshow(S);
title('Start');
subplot(2,2,2);
imshow(S2);
title('Finish');

Y=0.299*double(R)+0.587*double(G)+0.114*double(B);
U=-0.14713*double(R)-0.28886*double(G)+0.436*double(B)+128;
V=0.615*double(R)-0.51499*double(G)-0.10001*double(B)+128;

S2 = blockproc(S2, [8 8], @dct2);

DY=int16(DY);
DU=int16(DU);
DV=int16(DV);

S2 = blockproc(S2, [8 8], @idct2);

R=Y+1.13983*(V-128);
G=Y-0.39465*(U-128)-0.58060*(V-128);
B=Y+2.03211*(V-128);
