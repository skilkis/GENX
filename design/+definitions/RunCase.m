classdef RunCase
    %RUNCASE Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        x0              % Initial Design Vector
        N               % Number of Stages
        settings        % fmincon settings
    end
    
    properties
    end
    
    methods
        function obj = RunCase(N, x0, settings, data)
            %RUNCASE Construct an instance of this class
            %   Detailed explanation goes here
            obj.N = N;
            obj.x0 = x0;
            obj.settings = settings;
        end
        
        function optimum = optimize(obj)
            
        end
        
        function [c,ceq] = constraints(obj);
        end
        
        function [fval] = objective(obj);
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property1 + inputArg;
        end
    end
end

