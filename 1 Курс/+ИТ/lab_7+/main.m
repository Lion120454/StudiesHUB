ScreenSize = get(0,'ScreenSize');
handles.figure = figure('Position',[ScreenSize(3)/4,ScreenSize(4)/4,ScreenSize(3)/2,ScreenSize(4)/2]);

handles.E=uicontrol('Style','edit','Position',[100,50,50,20],'String', '90');
set(handles.E,'BackgroundColor',[1 1 1]);
set(handles.E,'HorizontalAlignment','left');
handles.B=uicontrol('Style','pushbutton', 'Position',[200,50,50,20], 'string', 'OK', 'Callback', 'Decode()');

A = imread('D:/хр/lab_7/jackal.png');
handles.A = A;
guidata(handles.figure, handles);

subplot(1,2,1);
imshow(A);
title('Base')



function Decode()
  handles=guidata(gcf);
  strParamVal = get(handles.E, 'String');
  disp(str2num(strParamVal));
  R = handles.A(:,:,1);
  G = handles.A(:,:,2);
  B = handles.A(:,:,3);
  strParamVal=str2double(strParamVal);



  Y=0.299*double(R)+0.587*double(G)+0.114*double(B);
  U=-0.14713*double(R)-0.28886*double(G)+0.436*double(B)+128;
  V=0.615*double(R)-0.51499*double(G)-0.10001*double(B)+128;

  DY = blockproc(Y,[8 8],@mydct);
  disp("DY = blockproc(Y,[8 8],@mydct)");
  DU = blockproc(U,[8 8],@mydct);
  disp("DU = blockproc(U,[8 8],@mydct)");
  DV = blockproc(V,[8 8],@mydct);
  disp("DV = blockproc(V,[8 8],@mydct)");
  disp(DY);
  MT=zeros(8,8);
  for i = 0:1:7
    for j = 0:1:7
      MT(i+1,j+1)=1+(i+j)*(100-strParamVal+1);

     endfor
  endfor
  disp(MT);
  DY=blockproc(DY,[8 8],@knv,MT);
  DV=blockproc(DV,[8 8],@knv,MT);
  DU=blockproc(DU,[8 8],@knv,MT);
  disp(DY);
  DY= round(DY);
  DU= round(DU);
  DV= round(DV);

  DY=blockproc(DY,[8 8],@iknv,MT);
  DV=blockproc(DV,[8 8],@iknv,MT);;
  DU=blockproc(DU,[8 8],@iknv,MT);

  DY = blockproc(DY,[8 8],@myidct);
  DU = blockproc(DU,[8 8],@myidct);
  DV = blockproc(DV,[8 8],@myidct);

  B(:,:,1)=DY+1.13983*(DV-128);
  B(:,:,2)=DY-0.39465*(DU-128)-0.58060*(DV-128);
  B(:,:,3)=DY+2.03211*(DU-128);
  B=uint8(B);
  subplot(1,2,2);
  imshow(B);
  title('Compressed')
endfunction


