##Пони
#загружаем изображение, делаем цветовые каналы и выделяем для него
M=imread("AJ.jpg");
R=M(:,:,1);
G=M(:,:,2);
B=M(:,:,3);
M_N=imresize(M,[32 32]);

%выводим каждый канал на консоли
figure
subplot(2,2,1);
imshow(M);
title('RGB');
subplot(2,2,2);
imshow(R);
title('Red');
subplot(2,2,3);
imshow(G);
title('Green');
subplot(2,2,4);
imshow(B);
title('Blue');

% преобразовываем из цветного пространства
Y=0.845*double(R)+0.6*double(G)+0.2*double(B);
U=-0.15*double(R)-0.35*double(G)+0.436*double(B)+128;
V=0.615*double(R)-0.6*double(G)-0.7*double(B)+128;
% прямое дискретно-косинусойдное преобразование
M_N = blockproc(M_N, [8 8], @dct2);
% из матрицы Y, U, and V получаем DY, DU and DV

% квантование dy, du и dv

DY=int16(DY); %округляем до целого
DU=int16(DU);
DV=int16(DV);

%обратное квантование
M_N = blockproc(M_N, [8 8], @idct2);
%обратно дискретно - косинусойдное преобразование здесь

%Из матрицы DY, DU и DV получаем Y, U и V
R=Y+2*(V-128);
G=Y-0.5*(U-128)-0.58060*(V-128);
B=Y+2.3*(V-128);

figure;
subplot(2,2,1);
imshow(M);
title('Image');
subplot(2,2,2);
imshow(M_N);
title('New image');
