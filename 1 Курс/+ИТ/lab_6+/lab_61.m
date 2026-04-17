function varargout = lab_61(varargin)
% lab_61 M-file for lab_61.fig
%      lab_61, by itself, creates a new lab_61 or raises the existing
%      singleton*.
%
%      H = lab_61 returns the handle to a new lab_61 or the handle to
%      the existing singleton*.
%
%      lab_61('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in lab_61.M with the given input arguments.
%
%      lab_61('Property','Value',...) creates a new lab_61 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before lab_61_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to lab_61_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help lab_61

% Last Modified by GUIDE v2.5 11-Jun-2022 11:24:14

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @lab_61_OpeningFcn, ...
                   'gui_OutputFcn',  @lab_61_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before lab_61 is made visible.
function lab_61_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to lab_61 (see VARARGIN)

% Choose default command line output for lab_61
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes lab_61 wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = lab_61_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in cGX.
function cGX_Callback(hObject, eventdata, handles)
% hObject    handle to cGX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if get (handles.cGX, 'Value') 
 set (gca, 'XGrid','on') 
else 
 set (gca, 'XGrid','off ') 
end


% Hint: get(hObject,'Value') returns toggle state of cGX


% --- Executes on button press in cGY.
function cGY_Callback(hObject, eventdata, handles)
% hObject    handle to cGY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if get (handles.cGY, 'Value') 
 set (gca, 'YGrid','on') 
else 
 set (gca, 'YGrid','off ') 
end

% Hint: get(hObject,'Value') returns toggle state of cGY



function eA_Callback(hObject, eventdata, handles)
% hObject    handle to eA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
a=str2double(get(hObject,'String')); 
if (a>0)
    set(hObject,'BackgroundColor','white');
    handles.a=a; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles)


% --- Executes during object creation, after setting all properties.
function eA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function eB_Callback(hObject, eventdata, handles)
% hObject    handle to eB (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
b=str2double(get(hObject,'String')); 
if (b>0)
    set(hObject,'BackgroundColor','white');
    handles.b=b; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles)


% --- Executes during object creation, after setting all properties.
function eB_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eB (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function eC_Callback(hObject, eventdata, handles)
% hObject    handle to eC (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
c=str2double(get(hObject,'String')); 
if (c>0)
    set(hObject,'BackgroundColor','white');
    handles.c=c; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles)


% --- Executes during object creation, after setting all properties.
function eC_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eC (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in StartBtn.
function StartBtn_Callback(hObject, eventdata, handles)
% hObject    handle to StartBtn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
a=handles.a;
b=handles.b;
c=handles.c;
p=(a+b+c)/2;
O1=(p*(p-a)*(p-b)*(p-c))^0.5;
O2=a+b+c;
h=(2*O1)/a;
an=(((1-(h/b)^2)^0.5)*b);
d1=h/an;
d2=h/(a-an);
x0=[0:0.1:a];
x1=[0:0.1:an];
x2=[an:0.1:a];
y1=((x1*d1));
y2=(h-((x2-an)*d2));
plot(x1,y1,x2,y2,x0,0)

set (handles.eO1, 'String', O1)
set (handles.eO2, 'String', O2)

if get (handles.cGX, 'Value') 
 set (gca, 'XGrid','on') 
else 
 set (gca, 'XGrid','off ') 
end
if get (handles.cGY, 'Value') 
 set (gca, 'YGrid','on') 
else 
 set (gca, 'YGrid','off ') 
end


set (hObject, 'Enable', 'of')
set (handles.ResetBtn, 'Enable', 'on')


% --- Executes on button press in ResetBtn.
function ResetBtn_Callback(hObject, eventdata, handles)
% hObject    handle to ResetBtn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set (hObject, 'Enable', 'of')
set (handles.StartBtn, 'Enable', 'on')
cla 
set (handles.eA, 'String', '')
set (handles.eB, 'String', '')
set (handles.eC, 'String', '')


% --- Executes during object creation, after setting all properties.
function eO1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eO1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes during object creation, after setting all properties.
function eO2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eO2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


