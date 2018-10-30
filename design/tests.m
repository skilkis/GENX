% obj = definitions.TestSubclass(2);
clc
clear all
close all
% 
% obj_test = definitions.MainClass(3);
% % 
% value = obj_test.fetcher();
% 
% obj_test.value = 8;
% obj_test.value = 10;
% 
inflow = definitions.FlowCondition('medium','gas',...
                                'T0', 288.15,...
                                'p', 101325);
                            
eta_tt = 0.92;
psi = 1.0;
phi = 1.2;
R = 0.5;
w = 604063.335547300;
omega = 35e3;

psi = 1.5;
R = 0.26;
phi = 1.81;
%                             
% stage = definitions.Stage(obj);

            
Stage = definitions.Stage(inflow, omega, psi, phi, R, w);
fhandle = Stage.plotVelocityDiagram();
