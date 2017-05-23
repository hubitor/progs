%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%      Analyse.m : effectue une analyse des r�sultats
%
% derni�re modification : 02.01.97 
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

res                   % lecture du fichier r�sultat
itmax=size(X,2)-1     % Nbre d'it�rations
X(:,itmax+1)

figure(1)
plot(0:itmax,FCT)
xlabel('it�rations'), ylabel('F(x)')
title('D�croissance de la fonction objectif')

figure(2)
plot(0:itmax,G)
xlabel('it�rations'), ylabel('|g(x)|')
title('D�croissance de la norme du gradient')

figure(3)
plot(0:itmax,X','k-')
xlabel('it�rations'), ylabel('Xi')
title('Convergence vers le minimum')