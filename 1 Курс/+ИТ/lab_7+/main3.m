figure;
I = imread('H:/ИТ/lab_7/jackal.png');
imshow(I);
I2 = rgb2gray(I);
I2 = im2double(I2);
I2 = blockproc(I2, [8 8], @myidct);



mask = [1 1 1 0 0 0 0 0
        1 1 0 0 0 0 0 0
        1 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 1
        0 0 0 0 0 0 1 1
        0 0 0 0 0 1 1 1];

I2 = blockproc(I2, [8 8], @mulMatrix, mask);

figure;
imshow(I2)

