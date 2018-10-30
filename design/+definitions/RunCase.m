classdef RunCase < handle
    %RUNCASE Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        x0              % Initial Design Vector
        N               % Number of Stages
        data            % Design Parameters
        options         % fmincon settings
    end
    
    properties (SetAccess = private, GetAccess = private)
        cache = struct();
    end
    
    properties (SetAccess = private)
        turbine
        x_final
        converged = false
    end
    
    methods
        function obj = RunCase(N, x0, options, data)
            %RUNCASE Construct an instance of this class
            %   Detailed explanation goes here
            obj.N = N;
            obj.x0 = x0;
            obj.options = options;
            obj.data = data;
            
            %Instantiating a Turbine
            obj.cache.x = obj.x0;
            Turbine = @definitions.Turbine;
            obj.cache.turbine = Turbine(obj.data.inflow,...
                                        x0.psi,...
                                        x0.phi,...
                                        x0.R, obj.N,...
                                        data.RPM,...
                                        data.PI);
        end
         
        function [c,ceq] = constraints(obj, x)
            ceq = [];
            obj.get_turbine(x);
            % Peripheral Speed Constraint
            c1 = obj.cache.turbine.stages{1,1}.U - 750;
%             c2 = obj
            c = c1;
        end
%         
        function fval = objective(obj, x)
            obj.get_turbine(x);
            fval = - obj.cache.turbine.eta_p / obj.cache.turbine.area;
        end
        
        function obj = optimize(obj)
            [x_out, ~] = fmincon(@obj.objective, obj.x0.data,...
                                 [],[],[],[],obj.x0.lb,obj.x0.ub,...
                                 @obj.constraints,obj.options);
            obj.x_final = x_out;
            obj.get_turbine(x_out) % Final access to ensure convergence
            obj.turbine = obj.cache.turbine;
            obj.converged = true;
        end
        
        function obj = get_turbine(obj,x)
            if obj.cache.x.data == x
                obj.cache.turbine = obj.cache.turbine;
            else
                obj.cache.x.data = x;
                Turbine = @definitions.Turbine;
                obj.cache.turbine = Turbine(obj.data.inflow,...
                                            obj.cache.x.psi,...
                                            obj.cache.x.phi,...
                                            obj.cache.x.R, obj.N,...
                                            obj.data.RPM,...
                                            obj.data.PI);
            end
        end
    end
end

