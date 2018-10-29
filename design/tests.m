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
% obj = definitions.FlowCondition('medium','gas',...
%                                 'T0', 288.15,...
%                                 'p', 101325);
%                             
% stage = definitions.Stage(obj);
% stage.inflow.T

x0 = definitions.DesignVector([0, 1, 3], {'lalal'});

% a1 = 2; a2 = 1.5; % define parameters first
options = optimset('Display', 'iter', 'Algorithm', 'sqp');
x = fmincon(@(x) x(0)^2 + x(1) ^2, x0.x0,[],[],[],[],[],[],[],options);

x0.lalal

x0.data(1) = 2;
