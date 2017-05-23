%++++++++++++++++++++++++++++++++++++++++++++++++++++++
% teste les solutions de GMRES, RFOM & MATLAB
%
% Update 12.12.96 pour GMRES4.FOR
%++++++++++++++++++++++++++++++++++++++++++++++++++++++

% Chargement data :

clear
load a
s_gmres; 
xxx=A\b';

% Affichage des deux solutions

[xxx x']
disp('   MATLAB - GMRES ')
disp(' ')
disp(['r�sidu GMRES  : ' num2str(norm(b'-A*x'))] )
disp(['r�sidu MATLAB : ' num2str(norm(b'-A*xxx))] )