function varargout = lab_65(varargin)
% lab_65 M-file for lab_65.fig
%      lab_65, by itself, creates a new lab_65 or raises the existing
%      singleton*.
%
%      H = lab_65 returns the handle to a new lab_65 or the handle to
%      the existing singleton*.
%
%      lab_65('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in lab_65.M with the given input arguments.
%
%      lab_65('Property','Value',...) creates a new lab_65 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before lab_65_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to lab_65_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help lab_65

% Last Modified by GUIDE v2.5 11-Jun-2022 11:27:57

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @lab_65_OpeningFcn, ...
                   'gui_OutputFcn',  @lab_65_OutputFcn, ...
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


% --- Executes just before lab_65 is made visible.
function lab_65_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to lab_65 (see VARARGIN)

% Choose default command line output for lab_65
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes lab_65 wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = lab_65_OutputFcn(hObject, eventdata, handles) 
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



function Ax_Callback(hObject, eventdata, handles)
% hObject    handle to Ax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ax as text
%        str2double(get(hObject,'String')) returns contents of Ax as a double
Ax_data=str2double(get(hObject,'String')); 
if (Ax_data>0)
    set(hObject,'BackgroundColor','white');
    handles.Ax_data=Ax_data; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles) 


% --- Executes during object creation, after setting all properties.
function Ax_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Bx_Callback(hObject, eventdata, handles)
% hObject    handle to Bx (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Bx as text
%        str2double(get(hObject,'String')) returns contents of Bx as a double
Bx_data=str2double(get(hObject,'String'));
if (Bx_data>0)
    set(hObject,'BackgroundColor','white');
    handles.Bx_data=Bx_data;
else
    set(hObject,'BackgroundColor','r')
end 
guidata (gcbo, handles) 


% --- Executes during object creation, after setting all properties.
function Bx_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Bx (see GCBO)
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
%  handles.Ax_data
%  handles.Ay_data
%  handles.Bx_data
%  handles.Ay_data
r1=((handles.Ax_data-handles.Ay_data)^2+(handles.Bx_data-handles.Ay_data)^2).^(1/2);

O1=abs(2*pi*r1);
x1=[-r1:0.2:r1]; 
y1=(((r1.^2)-(x1.^2)).^0.5)
y12=-y1;
plot(x1+handles.Ay_data,y1+handles.Ax_data,x1+handles.Ay_data,y12+handles.Ax_data)
O2=pi*r1^2

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

set (handles.resultat, 'String', O2)

set (handles.eOT, 'String', O1)

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
set (handles.eOT, 'String', '')
set (handles.resultat, 'String', '')




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



function eX_Callback(hObject, eventdata, handles)
% hObject    handle to eX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of eX as text
%        str2double(get(hObject,'String')) returns contents of eX as a double


% --- Executes during object creation, after setting all properties.
function eX_CreateFcn(hObject, eventdata, handles)
% hObject    handle to eX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function eA_Callback(hObject, eventdata, handles)
% hObject    handle to eA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of eA as text
%        str2double(get(hObject,'String')) returns contents of eA as a double


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



function By_Callback(hObject, eventdata, handles)
% hObject    handle to By (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of By as text
%        str2double(get(hObject,'String')) returns contents of By as a double
By_data=str2double(get(hObject,'String')); 
if (By_data>0)
    set(hObject,'BackgroundColor','white');
    handles.By_data=By_data; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles) 

% --- Executes during object creation, after setting all properties.
function By_CreateFcn(hObject, eventdata, handles)
% hObject    handle to By (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Ay_Callback(hObject, eventdata, handles)
% hObject    handle to Ay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ay as text
%        str2double(get(hObject,'String')) returns contents of Ay as a double
Ay_data=str2double(get(hObject,'String')); 
if (Ay_data>0)
    set(hObject,'BackgroundColor','white');
    handles.Ay_data=Ay_data; 
else
    set(hObject,'BackgroundColor','r')
end
guidata (gcbo, handles) 

% --- Executes during object creation, after setting all properties.
function Ay_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object creation, after setting all properties.
function resultat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to resultat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


