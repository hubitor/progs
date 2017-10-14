# -*- coding: latin-1 -*-
# $Id:  $

#################################################
#   Thick-walled sphere under internal pressure #
#===============================================#
# - Elasto-viscoplastic material                #
# - Mixed, kinematic or isotropic hardening     #
# - Perzyna viscoplasticity                     #
#################################################.

#0. Ent�te                                # Elle est obligatoire et toujours la m�me !
#=====================================================================================

from wrap import *                        #Importation des modules
import math

_metafor = None  #Analyse Metafor vide

#Interfa�age avec le logiciel Metafor 
#=====================================================================================
def getMetafor(_parameters={}): 
    global _metafor #Le mot cl� "global" fait r�f�rence � la variable _metafor d�finie � la ligne 17.
                    #Sinon la variable _metafor est une variable locale � la fonction getMetafor(). 
    if _metafor == None: 
        _metafor = buildDomain(_parameters)     #Cr�ation d'une analyse Metafor si _metafor n'existe pas.
    return _metafor

# Construction du dictionnaire contenant les param�tres
#=====================================================================================
def getParameters(_parameters={}):

    parameters= {} #Dictionnaire vide
    #Un dictionaire est un conteneur associatif. Il d�finit un lien unique entre une cl� de type string ('R1') et une valeur de type quelconque associ�e � cette cl� (100).
    #D�s lors, l'acc�s � un valeur stock�e dans le dictionnaire se fait au moyen de la cl� et de l'op�rateur [ ] : parameters['R1'].

    #1. D�finition des param�tres
    #=============================
    
    #1.1 G�ometrie                       #Param�tres de g�om�trie (; si plusieurs commandes sur la m�me ligne)
    #-------------
    parameters['R1'] = 100.                            #(mm)
    parameters['R2'] = 400.                

            
    #1.2 Maillage                        #Param�tres du maillage
    #-------------------------------------------------------------
    parameters['Nr']=20                     #Nombre de divisions radiales 
    parameters['No']=20                    #Nombre de divisions circonf�rentielles  

    #1.3 Discr�tisation temporelle        
    #-------------------------------------------------------------------------

    parameters['DeltatMax'] = 0.1                  #Pas de temps maximum  (sec) 
    parameters['DeltatInit'] = 0.1                 #Pas de temps initial  (sec)  
    parameters['Archi']   = 1                      #Param�tre du nombre d'archivage 

    parameters['MaxNumberMechanicalIterations'] =10                         #Nombre d'it�rations m�caniques par pas de temps
    parameters['ResidualMethodComputation'] =Method4ResidualComputation()   #Choix de la m�thode pour adimensionnaliser le r�sidu de NR
    parameters['ResidualTolerance'] =1.0E-6                                 #Choix de la tol�rance sur le r�sidu adimensionnel de NR  
    
    
    #1.4 Mat�riau                        #Param�tres mat�riau
    #----------------------------------------------------------------------
    parameters['Density']  = 8.190E-9                  #Densit� (T/mm3) non obligatoire ici, car c'est une �tude quasi-statique.
    parameters['Young'] = 200500.                      #MPa
    parameters['Nu'] = 0.3                              
    parameters['SigmaY_0'] = 200.                      #MPa
    parameters['SigmaY_Infty'] = 500.                  #MPa  
    parameters['Hard'] = 19000.                         #MPa
    parameters['Delta'] = 0.5
    parameters['Eta_Kin'] = 0.                         #Param�tre de recouvrance dynamique
    parameters['Visco_K'] = 0.                     #Param�tre de viscosit� plastique du mod�le de Persyna
    
    #CHOIX DU MATERIAU
    parameters['MaterialBehaviour'] = "ELASTOPLASTIC" #(ELASTOPLASTIC or ELASTOVISCOPLASTIC)
    parameters['HardeningModel'] = "NOHARDENING"        #(NOHARDENING, ISOTROPIC, KINEMATIC, MIXED)
    parameters['IsotropicHardening'] = "LINEAR"       #(LINEAR or NONLINEAR)
    parameters['KinematicHardening'] = "NONLINEAR"       #(LINEAR or NONLINEAR)
    
    #1.5 Chargement                   #Param�tres de la mise en charge
    #---------------------------------------------------------------------------------
    
    parameters['Umax'] = 0.8                   #D�placement radial impos� maximum (mm)
    parameters['TChaU'] = 1.0                        #Dur�e de mise en charge (sec) 
    parameters['NCycle'] = 1                        #Nombre de cycles de charge-d�charge

    parameters.update(_parameters)  #Mise � jour des param�tres 

    #On ajoute au dictionnaire "parameters" les cl�s et leurs valeurs associ�es d�finies dans "_parameters".
    #C'est une op�ration d'inclusion : 
    #Si une cl� du dictionnaire "_parameters" n'existe pas dans le dictionnaire "parameters", la cl� est cr��e et la valeur associ�e est copi�e dedans. 
    #Si une cl� du dictionnaire "_parameters" existe d�j� dans le dictionnaire "parameters", la valeur associ�e est copi�e dans la cl� commune. 
    return parameters  


# Construction du domaine 
#=====================================================================================
def buildDomain(_parameters={}):

    #Ouverture du domaine 
    #===============================================================
    metafor = Metafor() #Cr�ation d'une analyse Metafor
    parameters  = getParameters(_parameters) #R�cup�ration des param�tres de l'analysis
    domain = metafor.getDomain() #Acc�der au domaine
    
       
    #2. D�finition de la g�om�trie
    #===============================================================

    geometry = domain.getGeometry() #Acc�der � la g�om�trie
    geometry.setDimAxisymmetric()   #Mod�lisation axisym�trique

    #2.1 Points
    #---------------------------------------------------------------
    pointset = geometry.getPointSet()  #Acc�der aux points
    #D�finition des sommets du secteur annulaire
    P1 = pointset.define( 1,  parameters['R1'],  0.,  0.)
    P2 = pointset.define( 2,  parameters['R2'],  0.,  0.)
    P3 = pointset.define( 3,  parameters['R2']*math.cos(math.pi/4.0),  parameters['R2']*math.sin(math.pi/4.0),   0.)
    P4 = pointset.define( 4,  0.,  parameters['R2'],   0.)
    P5 = pointset.define( 5,  0.,  parameters['R1'],   0.)
    P6 = pointset.define( 6,  parameters['R1']*math.cos(math.pi/4.0),  parameters['R1']*math.sin(math.pi/4.0),   0.)
    
    #Axe de r�volution
    Axis1 = pointset.define( 7,  0.,  0.,   0.)
    Axis2 = pointset.define( 8,  0.,  0.,   1.)
    
    #2.2 Courbes
    #--------------------------------------------------------------
    curveset = geometry.getCurveSet()  #Acc�der aux courbes
    #D�finition des c�t�s du secteur annulaire 
    C1 = curveset.add( Line( 1, P1, P2) )
    C2 = curveset.add( Arc( 2, P2, P3, P4) )
    C3 = curveset.add( Line( 3, P4, P5) )
    C4 = curveset.add( Arc( 4, P5, P6, P1) )

    #2.3 Contours
    #-----------------------------------------------------------------
    wireset = geometry.getWireSet()  #Acc�der aux contours
    W1 = wireset.add(Wire(1, [curveset(1), curveset(2), curveset(3), curveset(4)])) #D�finir le contour 1 compos� des lignes 1 � 4
                                                                               #!SENS ANTIHORLOGIQUE!
    #2.4 Surface
    #----------------------------------------------------------------
    surfaceset = geometry.getSurfaceSet()  #Acc�der aux surfaces
    #D�finir un plan d'origine point 1 et de normale d�finie par le produit vectoriel entre le vecteur 
    #reliant le point 7 et le point 2 et celui reliant le point 7 et le point 4.
    Surf1 = surfaceset.add(Plane(1, Axis1, P2, P4))
    
    #2.5 Face � mailler
    #--------------------------------------------------------------------------
    sideset = geometry.getSideSet()  #Acc�der aux faces
    #D�finir la face 1 (partie maill�e plus tard) compos�e de l'int�rieur du contour 1 et de la surface plane 1
    S1 = sideset.add(Side(1,[wireset(1)]))
    S1.setSurface(Surf1)                                      
    
    #3. Maillage
    #============
    
    #3.1 D�finition du nombre de mailles sur chaque courbe  (2 c�t�s en vis a vis ont le m�me nombre de mailles)
    #-----------------------------------------------------
    SimpleMesher1D(C1).execute(parameters['Nr'])                               #Nr mailles sur la courbe 1
    SimpleMesher1D(C2).execute(parameters['No'])                               #No mailles sur la courbe 2
    SimpleMesher1D(C3).execute(parameters['Nr'])                               #Nr mailles sur la courbe 3
    SimpleMesher1D(C4).execute(parameters['No'])                               #No mailles sur la courbe 4

    #3.2 D�finition de la face � mailler
    #------------------------------------
    TransfiniteMesher2D(S1).execute2( (1,2,3,4) )  #Indiquer quelles lignes correspondent aux c�t�s du maillage de la face 1  

    #4. Lois de comportement
    #========================
    
    #4.1 D�finition du mat�riau et #4.2 D�finition des lois d'�crouissage
    #--------------------------------------------------------------------
    
    materset = domain.getMaterialSet()  #Acc�der aux comportements du mat�riau
    lawset = domain.getMaterialLawSet()  #Acc�der aux lois mat�rielles
    
    if (parameters['MaterialBehaviour'] == "ELASTOPLASTIC"): 
        if(parameters['HardeningModel'] == "NOHARDENING"):
            material1 = materset.define (1, EvpIsoHHypoMaterial)    #Cr�er un mat�riau �lasto-plastique num�ro 1 � �crouissage isotrope
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,1)                #Num�ro de la loi d'�crouissage isotrope  1
            
            lawset1 = lawset.define(1, LinearIsotropicHardening)  #Ecrouissage isotrope lin�aire 1
            lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
            lawset1.put(IH_H,       0.0)              #Sans Ecrouissage : Hard = 0.0
            
            print "Elasto-plastic material with no hardening"
        elif(parameters['HardeningModel'] == "ISOTROPIC"):
            material1 = materset.define (1, EvpIsoHHypoMaterial)    #Cr�er un mat�riau �lasto-plastique num�ro 1 � �crouissage isotrope
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,1)                #Num�ro de la loi d'�crouissage isotrope  1
            
            if(parameters['IsotropicHardening'] == "LINEAR"): 
                lawset1 = lawset.define(1, LinearIsotropicHardening)                    #Ecrouissage isotrope lin�aire 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_H,       parameters['Hard'])
                
                print "Elasto-plastic material with a linear isotropic hardening"
            elif(parameters['IsotropicHardening'] == "NONLINEAR"): 
                lawset1 = lawset.define(1, SaturatedIsotropicHardening)                 #Ecrouissage isotrope non-lin�aire de Voce 1
                lawset1.put(IH_SIGEL,parameters['SigmaY_0'])
                lawset1.put(IH_Q, parameters['SigmaY_Infty']-parameters['SigmaY_0'])
                lawset1.put(IH_KSI,parameters['Hard']/(parameters['SigmaY_Infty']-parameters['SigmaY_0']))
                
                print "Elasto-plastic material with a non-linear isotropic hardening"
            else:
                raise Exception('Unknown Isotropic Hardening =', IsotropicHardening)
        elif(parameters['HardeningModel'] == "KINEMATIC"):
            material1 = materset.define (1, EvpMixtHHypoMaterial)   #Cr�er un mat�riau �lasto-plastique num�ro 1 � �crouissage mixte
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,1)                #Num�ro de la loi d'�crouissage isotrope  (1)
            material1.put(KH_NB,1)                    #Nombre d'�crouissages cin�matiques
            material1.put(KH_NUM1,2)                  #Num�ro de la loi d'�crouissage cin�matique (2)
            
            lawset1 = lawset.define(1, LinearIsotropicHardening)  #Ecrouissage isotrope lin�aire 1
            lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
            lawset1.put(IH_H,       0.0)              #Sans Ecrouissage Isotrope : Hard_Iso = 0.0
            if(parameters['KinematicHardening'] == "LINEAR"): 
                lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                lawset2.put(KH_H, parameters['Hard'])
                
                print "Elasto-plastic material with a linear kinematic hardening"
            elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                lawset2.put(KH_H, parameters['Hard'])
                lawset2.put(KH_B, parameters['Eta_Kin'])
                
                print "Elasto-plastic material with a non-linear kinematic hardening"
            else:
                raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
        elif parameters['HardeningModel'] == "MIXED" :
            material1 = materset.define (1, EvpMixtHHypoMaterial)   #Cr�er un mat�riau �lasto-viscoplastique num�ro 1 � �crouissage mixte
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,1)                #Num�ro de la loi d'�crouissage isotrope  (1)
            material1.put(KH_NB,1)                    #Nombre d'�crouissages cin�matiques
            material1.put(KH_NUM1,2)                  #Num�ro de la loi d'�crouissage cin�matique (2)
            
            #D�finition des coefficients de pond�ration des �crouissages isotropes et cin�matiques
            
            Hard_Iso = parameters['Hard']*(1.0-parameters['Delta'])                   
            Hard_Kin = parameters['Hard']*parameters['Delta']   
            
            if(parameters['IsotropicHardening'] == "LINEAR"): 
                lawset1 = lawset.define(1, LinearIsotropicHardening)                    #Ecrouissage isotrope lin�aire 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_H,       Hard_Iso)
                
                if(parameters['KinematicHardening'] == "LINEAR"): 
                    lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                    lawset2.put(KH_H, Hard_Kin)
                    
                    print "Elasto-plastic material with a mixte hardening : linear isotropic hardening and linear kinematic hardening"
                elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                    lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                    lawset2.put(KH_H, Hard_Kin)
                    lawset2.put(KH_B, parameters['Eta_Kin'])
                    
                    print "Elasto-plastic material with a mixte hardening : linear isotropic hardening and non-linear kinematic hardening"
                else:
                    raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
            elif(parameters['IsotropicHardening'] == "NONLINEAR"):
                lawset1 = lawset.define(1, SaturatedIsotropicHardening)                 #Ecrouissage isotrope non-lin�aire de Voce 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_Q, parameters['SigmaY_Infty']-parameters['SigmaY_0'])
                lawset1.put(IH_KSI,Hard_Iso/(parameters['SigmaY_Infty']-parameters['SigmaY_0']))
                if(parameters['KinematicHardening'] == "LINEAR"): 
                
                    lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                    lawset2.put(KH_H, Hard_Kin)
                    
                    print "Elasto-plastic material with a mixte hardening : non-linear isotropic hardening and linear kinematic hardening"
                elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                
                    lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                    lawset2.put(KH_H, Hard_Kin)
                    lawset2.put(KH_B, parameters['Eta_Kin'])
                    
                    print "Elasto-plastic material with a mixte hardening : non-linear isotropic hardening and non-linear kinematic hardening"
                else:
                    raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
            else:
                raise Exception('Unknown Isotropic Hardening =', IsotropicHardening)
        else: 
            raise Exception('Unknown Hardening Model =', HardeningModel)
    elif(parameters['MaterialBehaviour'] == "ELASTOVISCOPLASTIC"): 
        lawset3 = lawset.define (3, PerzynaYieldStress)                         #Loi de viscosit� plastique de Perzyna 3
        lawset3.put(PERZYNA_K, parameters['Visco_K'])
        lawset3.put(PERZYNA_M, 1.)
        lawset3.put(PERZYNA_N, 0.)
        lawset3.put(IH_NUM, 1)                                   #Num�ro de l'�crouissage isotrope (1)
        if(parameters['HardeningModel'] == "NOHARDENING"):
            material1 = materset.define (1, EvpIsoHHypoMaterial)    #Cr�er un mat�riau �lasto-viscoplastique num�ro 1 � �crouissage isotrope
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,3)                #Num�ro de la loi de viscosit� plastique (3)
            
            lawset1 = lawset.define(1, LinearIsotropicHardening)  #Ecrouissage isotrope lin�aire 1
            lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
            lawset1.put(IH_H,       0.0)              #Sans Ecrouissage : Hard = 0.0
            
            print "Elasto-viscoplastic material with no hardening"
        elif(parameters['HardeningModel'] == "ISOTROPIC"):
            material1 = materset.define (1, EvpIsoHHypoMaterial)    #Cr�er un mat�riau �lasto-viscoplastique num�ro 1 � �crouissage isotrope
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,3)                #Num�ro de la loi de viscosit� plastique (3)
            
            if(parameters['IsotropicHardening'] == "LINEAR"): 
                lawset1 = lawset.define(1, LinearIsotropicHardening)                    #Ecrouissage isotrope lin�aire 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_H,       parameters['Hard'])
                
                print "Elasto-viscoplastic material with a linear isotropic hardening"
                
            elif(parameters['IsotropicHardening'] == "NONLINEAR"): 
                lawset1 = lawset.define(1, SaturatedIsotropicHardening)                 #Ecrouissage isotrope non-lin�aire de Voce 1
                lawset1.put(IH_SIGEL,parameters['SigmaY_0'])
                lawset1.put(IH_Q, parameters['SigmaY_Infty']-parameters['SigmaY_0'])
                lawset1.put(IH_KSI,parameters['Hard']/(parameters['SigmaY_Infty']-parameters['SigmaY_0']))
                
                print "Elasto-viscoplastic material with a non-linear isotropic hardening"
                
            else:
                raise Exception('Unknown Isotropic Hardening =', IsotropicHardening)
        elif(parameters['HardeningModel'] == "KINEMATIC"):
            material1 = materset.define (1, EvpMixtHHypoMaterial)   #Cr�er un mat�riau �lasto-viscoplastique num�ro 1 � �crouissage mixte
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,3)                #Num�ro de la loi de viscosit� plastique (3)
            material1.put(KH_NB,1)                    #Nombre d'�crouissages cin�matiques
            material1.put(KH_NUM1,2)                  #Num�ro de la loi d'�crouissage cin�matique (2)
            
            lawset1 = lawset.define(1, LinearIsotropicHardening)  #Ecrouissage isotrope lin�aire 1
            lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
            lawset1.put(IH_H,       0.0)              #Sans Ecrouissage Isotrope : Hard_Iso = 0.0
            
            if(parameters['KinematicHardening'] == "LINEAR"): 
                lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                lawset2.put(KH_H, parameters['Hard'])
                
                print "Elasto-viscoplastic material with a linear kinematic hardening"
                
            elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                lawset2.put(KH_H, parameters['Hard'])
                lawset2.put(KH_B, parameters['Eta_Kin'])
                
                print "Elasto-viscoplastic material with a non-linear kinematic hardening"
                
            else:
                raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
        elif parameters['HardeningModel'] == "MIXED" :
            material1 = materset.define (1, EvpMixtHHypoMaterial)   #Cr�er un mat�riau �lasto-viscoplastique num�ro 1 � �crouissage mixte
            material1.put(MASS_DENSITY,    parameters['Density'])   #Masse volumique
            material1.put(ELASTIC_MODULUS, parameters['Young'])     #Module de Young
            material1.put(POISSON_RATIO,   parameters['Nu'])        #Coefficient de Poisson
            material1.put(YIELD_NUM,3)                #Num�ro de la loi de viscosit� plastique (3)
            material1.put(KH_NB,1)                    #Nombre d'�crouissages cin�matiques
            material1.put(KH_NUM1,2)                  #Num�ro de la loi d'�crouissage cin�matique (2)
            
            #D�finition des coefficients de pond�ration des �crouissages isotropes et cin�matiques
            
            Hard_Iso = parameters['Hard']*(1.0-parameters['Delta'])                   
            Hard_Kin = parameters['Hard']*parameters['Delta']   
            
            if(parameters['IsotropicHardening'] == "LINEAR"): 
                lawset1 = lawset.define(1, LinearIsotropicHardening)                    #Ecrouissage isotrope lin�aire 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_H,       Hard_Iso)
                
                if(parameters['KinematicHardening'] == "LINEAR"): 
                    lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                    lawset2.put(KH_H, Hard_Kin)
                    
                    print "Elasto-viscoplastic material with a mixte hardening : linear isotropic hardening and linear kinematic hardening"
                    
                elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                    lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                    lawset2.put(KH_H, Hard_Kin)
                    lawset2.put(KH_B, parameters['Eta_Kin'])
                    
                    print "Elasto-viscoplastic material with a mixte hardening : linear isotropic hardening and non-linear kinematic hardening"
                    
                else:
                    raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
                
            elif(parameters['IsotropicHardening'] == "NONLINEAR"):
                lawset1 = lawset.define(1, SaturatedIsotropicHardening)                 #Ecrouissage isotrope non-lin�aire de Voce 1
                lawset1.put(IH_SIGEL,   parameters['SigmaY_0'])
                lawset1.put(IH_Q, parameters['SigmaY_Infty']-parameters['SigmaY_0'])
                lawset1.put(IH_KSI,Hard_Iso/(parameters['SigmaY_Infty']-parameters['SigmaY_0']))
                
                if(parameters['KinematicHardening'] == "LINEAR"): 
                    lawset2 = lawset.define(2, DruckerPragerKinematicHardening)     #Ecrouissage cin�matique lin�aire de Drucker Prager  2                                                        
                    lawset2.put(KH_H, Hard_Kin)
                    
                    print "Elasto-viscoplastic material with a mixte hardening : non-linear isotropic hardening and linear kinematic hardening"
                    
                elif(parameters['KinematicHardening'] == "NONLINEAR"): 
                    lawset2 = lawset.define(2, ArmstrongFrederickKinematicHardening)     #Ecrouissage cin�matique non-lin�aire d'Armstrong Fr�d�rick 2                                                          
                    lawset2.put(KH_H, Hard_Kin)
                    lawset2.put(KH_B, parameters['Eta_Kin'])
                    
                    print "Elasto-viscoplastic material with a mixte hardening : non-linear isotropic hardening and non-linear kinematic hardening"
                    
                else:
                    raise Exception('Unknown Kinematric Hardening =', KinematicHardening)
            
            else:
                raise Exception('Unknown Isotropic Hardening =', IsotropicHardening)
        else: 
            raise Exception('Unknown Hardening Model =', HardeningModel)
    else : 
        raise Exception('Unknown Material Behaviour =', MaterialBehavour)

    #5. D�finition des �l�ments finis volumiques
    #==============================================================================
    
    #5.1 D�finition des propri�t�s des �l�ments finis volumiques
    #------------------------------------------------------------------------------
    prp1 = ElementProperties(Volume2DElement)                     #Cr�er une propri�t� prp1 pour les �l�ments finis volumiques
                                                                  #et d�finir le type d'�l�ments finis
                                                                  
    prp1.put(MATERIAL, 1)                                           #Num�ro du mat�riau associ� aux �l�ments finis
    prp1.put(STIFFMETHOD, STIFF_ANALYTIC)                           #M�thode de calcul de la matrice de raideur tangente 
    prp1.put(CAUCHYMECHVOLINTMETH, VES_CMVIM_SRIPR)                 #Sous int�gration s�lective avec report de pression
    
    #5.2 G�n�ration des �l�ments finis volumiques sur le maillage
    #-------------------------------------------------------------------------------
    interactionset = domain.getInteractionSet()  #Acc�der � la gestion des interactions
    
    app1 = FieldApplicator(1)                                       #Cr�ation d'un g�n�rateur (num�ro 1) d'�l�ments finis volumiques
    app1.push(sideset(1))                                           #Support = face 1
    app1.addProperty(prp1)                                          #Assigner la propri�t� prp1 aux futurs �l�ments volumiques de la face 1
    interactionset.add(app1)                                        #Ajouter le g�n�rateur 1 � la liste des interactions
    
    #6. Fixations
    #==============================================================================
    loadingset=domain.getLoadingSet()  #Acc�der � la gestion des Dofs impos�s
    
    #On bloque le d�placement normal sur les plans de sym�trie horizontale et verticale de la sph�re : 
    fix1 = loadingset.define(C1,Field1D(TY,RE),0.)
    fix2 = loadingset.define(C3,Field1D(TX,RE),0.)
    
    #7. Chargement (par un d�placement impos�)
    #===============================================================================
    
    fctU = PieceWiseLinearFunction()    #Fonction d'amplitude unitaire d�crivant l'�volution temporelle de la mise en charge
    fctU.setData(0., 0. )                 
    
    #D�finition d'une fonction en dents de scie sur NCycle
    for i in range (parameters['NCycle']):               #i in [0 1 ... NCycle-2 NCycle-1]          
        fctU.setData((4*i+1)*parameters['TChaU'],  1.)
        fctU.setData((4*i+3)*parameters['TChaU'],  -1.)
        fctU.setData((4*i+4)*parameters['TChaU'], 0.) 

    #On impose un d�placement radial sur la face interne de la sphere : u_r(t)=Umax*fctU :
    loadingset.defineRad(C4, Field3D(TXTYTZ,RE), Axis1, Axis2, parameters['Umax'], fctU)
    
    #8. Sch�ma d'int�gration temporelle
    #==================================
    
    #8.1 Gestion des pas de temps
    #-----------------------------
    tsm = metafor.getTimeStepManager()                              #Acc�der � la gestion des pas de temps
    
    tsm.setInitialTime(0.0,   parameters['DeltatInit'])                #Commencer en t=0 avec un pas de temps initial = DeltatInit
    for i in range (parameters['NCycle']*4):                                         #i in [0 1 ... 4*NCycle-2 4*NCycle-1]
       tsm.setNextTime((i+1)*parameters['TChaU'], parameters['Archi'], parameters['DeltatMax'])                          
    #Aller jusqu'� t=(i+1)*TChaU (s�quences principales d'un cycle de charge et d�charge) en archivant "Archi" r�sultats sur cette s�quence et 
    #avec un pas de temps maximal de DeltatMax. Si Archi = 1, on archive les instants aux extr�mit�s de chaque intervalle de temps [ti ti+1].
    #Par contre si Archi = 2, on archive les instants aux extr�mit�s de chaque intervalle de temps [ti ti+1] et on force le passage de l'algorithme � l'instant 
    #(ti+1-ti)/2 pour archiver les r�sultats � cet instant.
        
    #8.2 Gestion des it�rations m�caniques
    #----------------------------------------------
    mim = metafor.getMechanicalIterationManager()   #Acc�der � la gestion des it�rations m�caniques
    
    mim.setMaxNbOfIterations(parameters['MaxNumberMechanicalIterations'])              #Nombre d'it�rations m�caniques par pas de temps
    mim.setResidualTolerance(parameters['ResidualTolerance'])                          #Pr�cision sur le r�sidu du NR de 1.E-6
    mim.setResidualComputationMethod(parameters['ResidualMethodComputation'])          #M�thode pour adimensionnaliser le r�sidu
    
        
    #8.3 Choix du sch�ma d'int�gration temporelle
    #---------------------------------------------
    metafor.setIntegerData(MDE_NDYN, 0)  #Analyse quasi-statique (facultatif car valeur par d�faut)
    
    #9. Archivage des courbes sur le disque dur
    #==========================================
    
    valuesmanager = metafor.getValuesManager()          #Acc�der � la gestion des courbes
    
    valuesmanager.add(1, MiscValueExtractor(metafor,EXT_T),'time')
    #Archiver le temps en courbe num�ro 1 et nommer time le fichier d'archivage du temps
    valuesmanager.add(2, IFNodalValueExtractor(P1, IF_CRITERION),'SigmaVMInt' )
    #Archiver la contrainte �quivalente de Von Mises extrapol�e au noeud inf�rieur gauche en courbe num�ro 2
    #et nommer SigmaVMInt le fichier d'archivage de la grandeur aux diff�rents instants
    valuesmanager.add(3, IFNodalValueExtractor(P2, IF_CRITERION),'SigmaVMExt' )
    #Archiver la contrainte �quivalente de Von Mises extrapol�e au noeud inf�rieur droit en courbe num�ro 3
    #et nommer SigmaVMInt le fichier d'archivage de la grandeur aux diff�rents instants
    valuesmanager.add(4, DbNodalValueExtractor(P1, Field1D(TX,RE)),'u' )
    #Archiver le d�placement radial au noeud inf�rieur gauche en courbe num�ro 4
    #et nommer u le fichier d'archivage de la grandeur aux diff�rents instants    
    valuesmanager.add(5, DbNodalValueExtractor(C3, Field1D(TX,GF1)), SumOperator(),'R' )
    #Archiver la force de r�action � le plan de coupe verticale de la sphere en courbe num�ro 5
    #et nommer R le fichier d'archivage de la grandeur aux diff�rents instants
    valuesmanager.add(6, IFNodalValueExtractor(P1, IF_EPL),'EPLInt' )
    #Archiver la d�formation plastique �quivalente extrapol�e au noeud inf�rieur gauche en courbe num�ro 6
    #et nommer EPLInt le fichier d'archivage de la grandeur aux diff�rents instants
    valuesmanager.add(7, IFNodalValueExtractor(P2, IF_EPL),'EPLExt' )
    #Archiver la d�formation plastique �quivalente extrapol�e au noeud inf�rieur droit en courbe num�ro 7
    #et nommer EPLExt le fichier d'archivage de la grandeur aux diff�rents instants


                                                        
    #10. Visualisation en temps r�el des courbes            (FACULTATIF mais utile)
    #===========================================
    # On met les commandes de visualisation entre try et except pour g�rer automatiquement les cas 
    # o� le logiciel Metafor n'a pas �t� compil� avec la visualisation et ne poss�de donc pas l'objet VizWin.
    
    try:
        #Demander d'ouvrir une fen�tre VizWin avec deux graphes : 
        #La courbe 1 nomm� SigmaVMInt affiche les valeurs archiv�es pour la courbe 2 (SigmaVM au noeud inf�rieur gauche) 
        #en fonction de celles archiv�es pour la courbe 1 (temps); 
        #La courbe 2 nomm� SigmaVMExt affiche les valeurs archiv�es pour la courbe 3 (SigmaVM au noeud inf�rieur droit)
        #en fonction de celles pour la courbe 1 (temps); 
        
        dataCurve1 = VectorDataCurve(1, valuesmanager.getDataVector(1), valuesmanager.getDataVector(2),'SigmaVMInt')
        dataCurve2 = VectorDataCurve(2, valuesmanager.getDataVector(1), valuesmanager.getDataVector(3),'SigmaVMExt')
        dataCurveSet1 = DataCurveSet()                     
        dataCurveSet1.add(dataCurve1)                     
        dataCurveSet1.add(dataCurve2)                      
        winc1 = VizWin()                                   
        winc1.add(dataCurveSet1)                           
        metafor.addObserver(winc1)                        
    
        #Demander d'ouvrir une nouvelle fen�tre VizWin avec un graphe : 
        #La courbe 1 nomm� R affiche les valeurs archiv�es pour la courbe 5 (Force de r�action totale) 
        #en fonction de celles archiv�es pour la courbe 1 (temps); 
        
        dataCurve3 = VectorDataCurve(3, valuesmanager.getDataVector(1), valuesmanager.getDataVector(5),'R')
        dataCurveSet2 = DataCurveSet()                     
        dataCurveSet2.add(dataCurve3)                       
        winc2 = VizWin()                                   
        winc2.add(dataCurveSet2)
        metafor.addObserver(winc2)
        
        #Demander d'ouvrir une nouvelle fen�tre VizWin avec un graphe : 
        #La courbe 1 nomm� u affiche les valeurs archiv�es pour la courbe 4 (D�placement radial impos� au noeud inf�rieur gauche) 
        #en fonction de celles archiv�es pour la courbe 1 (temps);     
        
        dataCurve4 = VectorDataCurve(4, valuesmanager.getDataVector(1), valuesmanager.getDataVector(4),'u')
        dataCurveSet3 = DataCurveSet()                     
        dataCurveSet3.add(dataCurve4)                       
        winc3 = VizWin()                                  
        winc3.add(dataCurveSet3)
        metafor.addObserver(winc3)
        
        #Demander d'ouvrir une nouvelle fen�tre VizWin avec deux graphes : 
        #La courbe 1 nomm� EPLInt affiche les valeurs archiv�es pour la courbe 6 (EPL au noeud inf�rieur gauche) 
        #en fonction de celles archiv�es pour la courbe 1 (temps); 
        #La courbe 2 nomm� EPLExt affiche les valeurs archiv�es pour la courbe 7 (EPL au noeud inf�rieur droit)
        #en fonction de celles pour la courbe 1 (temps); 
        
        dataCurve5 = VectorDataCurve(5, valuesmanager.getDataVector(1), valuesmanager.getDataVector(6),'EPLInt' )
        dataCurve6 = VectorDataCurve(6, valuesmanager.getDataVector(1), valuesmanager.getDataVector(7),'EPLExt' )
        dataCurveSet4 = DataCurveSet()                     
        dataCurveSet4.add(dataCurve5)                      
        dataCurveSet4.add(dataCurve6)                      
        winc4 = VizWin()                                   
        winc4.add(dataCurveSet4)                           
        metafor.addObserver(winc4)                          
        
    except NameError:
        pass
    
    #L'objet TestSuiteChecker de Metafor �crit par d�faut un certain nombre de grandeurs caract�ristiques du d�roulement du calcul, � la fin du calcul. 
    #Il est possible d'ajouter des valeurs sp�cifiques extraites du probl�me (mesures caract�ristiques du probl�me). 
    #La personnalisation du TestSuiteChecker au probl�me se fait � l'aide des fonctions suivantes :     
    testSuite = metafor.getTestSuiteChecker()
    testSuite.checkExtractor(2)                         #Affiche � l'�cran la valeur finale de la courbe archiv�e 2 (SigmaVMInt)
    testSuite.checkExtractor(5)                         #Affiche � l'�cran la valeur finale de la courbe archiv�e 5 (Force de r�action totale)                                
    
    return metafor