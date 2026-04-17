function varargout = lab_64(varargin)
% lab_64 M-file for lab_64.fig
%      lab_64, by itself, creates a new lab_64 or raises the existing
%      singleton*.
%
%      H = lab_64 returns the handle to a new lab_64 or the handle to
%      the existing singleton*.
%
%      lab_64('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in lab_64.M with the given input arguments.
%
%      lab_64('Property','Value',...) creates a new lab_64 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before lab_64_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to lab_64_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help lab_64

% Last Modified by GUIDE v2.5 11-Jun-2022 11:27:18

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @lab_64_OpeningFcn, ...
                   'gui_OutputFcn',  @lab_64_OutputFcn, ...
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


% --- Executes just before lab_64 is made visible.
function lab_64_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to lab_64 (see VARARGIN)

% Choose default command line output for lab_64
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes lab_64 wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = lab_64_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in cbGridX.
function cbGridX_Callback(hObject, eventdata, handles)
% hObject    handle to cbGridX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of cbGridX
if get (handles.cbGridX, 'Value') 
 set (gca, 'XGrid','on') 
else 
 set (gca, 'XGrid','off ') 
end
if get (handles.cbGridY, 'Value') 
 set (gca, 'YGrid','on') 
else 
 set (gca, 'YGrid','off ') 
end


% --- Executes on button press in cbGridY.
function cbGridY_Callback(hObject, eventdata, handles)
% hObject    handle to cbGridY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: get(hObject,'Value') returns toggle state of cbGridY
if get (handles.cbGridX, 'Value') 
 set (gca, 'XGrid','on') 
else 
 set (gca, 'XGrid','off ') 
end
if get (handles.cbGridY, 'Value') 
 set (gca, 'YGrid','on') 
else 
 set (gca, 'YGrid','off ') 
end



function Ed1_Callback(hObject, eventdata, handles)
% hObject    handle to Ed1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ed1 as text
%        str2double(get(hObject,'String')) returns contents of Ed1 as a double
d1=str2double(get(hObject,'String')); 
if (d1>0)
    set(hObject,'BackgroundColor','white');
    handles.d1=d1; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles) 


% --- Executes during object creation, after setting all properties.
function Ed1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ed1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Ed2_Callback(hObject, eventdata, handles)
% hObject    handle to Ed2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ed2 as text
%        str2double(get(hObject,'String')) returns contents of Ed2 as a double
d2=str2double(get(hObject,'String'));
if (d2>0)
    set(hObject,'BackgroundColor','white');
    handles.d2=d2;
else
    set(hObject,'BackgroundColor','r')
end 
guidata (gcbo, handles) 


% --- Executes during object creation, after setting all properties.
function Ed2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ed2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in BtnStart.
function BtnStart_Callback(hObject, eventdata, handles)
% hObject    handle to BtnStart (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

d1=handles.d1;
O1=(d1^2)/2;
O2=(O1^0.5)*4;
n=O2/4
x1=[0:0.1:n]; 
y1=[0:0.1:n];
plot(x1,0,x1,n,0,y1,n,y1)
set (handles.eOT, 'String', O1)
set (handles.eP, 'String', O2)

set (hObject, 'Enable', 'of')
set (handles.BtnReset, 'Enable', 'on')



% --- Executes on button press in BtnReset.
function BtnReset_Callback(hObject, eventdata, handles)
% hObject    handle to BtnReset (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set (hObject, 'Enable', 'of')
set (handles.BtnStart, 'Enable', 'on')
cla 
set (handles.Ed1, 'String', '')
set (handles.Ed2, 'String', '')
set (handles.eOT, 'String', '')




function eOT_Callback(hObject, eventdata, handles)
% hObject    handle to eOT (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of eOT as text
%        str2double(get(hObject,'String')) returns contents of eOT as a double


% --- Executes during object creation, after setting all properties.
function eOT_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eOT (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object creation, after setting all properties.
function eP_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eP (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


