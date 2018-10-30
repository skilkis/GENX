classdef Turbine < definitions.Constants
    %TURBINE Repeating Stage Turbine
    %   Detailed explanation goes here
    
    properties
        inflow                  % Known Inflow State Variables
        psi                     % Work Coefficient [-]
        phi                     % Flow Coefficient [-]
        R                       % Degree of Reaction [-]
        N                       % Number of Stages [-]
        RPM                     % Revolutions Per Minute [rev/min]
        PI                      % Expansion Ratio [-]
    end

    properties (SetAccess = private)
        eta_p                   % Polytropic Efficiency [-]
        converged = false       % If Polytropic Efficiency has Converged
        stages                  % Struct containing built Stages
        stages_complete = false % If stages have been fully built
        mach_known = false      % If mach number is known
    end
    
    properties (Dependent)
        omega                   % Angular Velocity at Mean Radius [rad/s]
        outflow                 % Outflow state variables
        w                       % Specific Work per Stage
    end
    
    methods
        function obj = Turbine(varargin)
            % Creates optional arguments for all state variables
            args = inputParser; % Analyzes passed arguments
            
            addRequired(args, 'inflow', @definitions.Validators.validFlow)
%             addRequired(args, 'psi');
%             addRequired(args, 'phi');
%             addRequired(args, 'R');
%             addRequired(args, 'N');
%             addRequired(args, 'RPM')
%             addRequired(args, '
            
            exclude = fieldnames(definitions.Constants)';
            exclude = [exclude, 'inflow', 'outflow', 'omega', 'eta_p',...
                       'w', 'stages', 'converged', 'stages_complete',...
                       'mach_known'];
            for prop = fieldnames(obj)'
                if ~any(strcmp(exclude, prop{:}))
                    addRequired(args, prop{:})
                end
            end
              
            % Sets result of all optional arguments for current object
            parse(args, varargin{:});   
            for field = fieldnames(args.Results)'
                obj.(field{:}) = args.Results.(field{:});
            end
            
            % Calculates Polytropic Efficiency on Entry
            obj = obj.calcPolytropic();
            
            % Builds all stages
            obj = obj.buildStages();
        end

    end

    methods
        %% Dependent Property Getters
        function value = get.omega(obj)
            value = obj.RPM * (2*pi) / 60;
        end
        
        function value = get.outflow(obj)
            % Calculates the Outflow Total Temperature of the Turbine 
            % utilizing the Polytropic small-stage efficiency T0_out is 
            % in SI Kelvin [K]. Other state variables are passed to a 
            % :matlab:class:`FlowCondition` object. If the stages are fully
            % constructed, then the outflow of the final stage is returned.
            if obj.stages_complete
                value = obj.stages{end,1}.outflow;
            else
                in = obj.inflow;
                T0_out = in.T0*(1/obj.PI)^((in.kappa-1)/in.kappa*obj.eta_p);
                value = definitions.FlowCondition('m_dot', in.m_dot,...
                                                  'medium', in.medium,...
                                                  'T0', T0_out);
            end
        end

        function value = get.w(obj)
            % Calculates the specific work and divides it equally among
            % the stages. Repeating stage assumption.
            Ws = obj.inflow.cp*(obj.inflow.T0 - obj.outflow.T0);
            value = Ws/obj.N; % Dividing specific work equally
        end
        
    end

    methods (Access = private)
        function residual = objective(obj, eta_p_hat)

            % Locally updating p_hat (Values update due to dependency)
            obj.eta_p = eta_p_hat;

            p_start = obj.inflow.p0; % Inflow Total Pressure
            T0_in = obj.inflow.T0; T0_out = obj.outflow.T0;

            % Total-to-Total Efficiency from Stage Calculations
            stage = definitions.Stage(obj.inflow, obj.omega, obj.psi,...
                                    obj.phi, obj.R, obj.w);
            eta_tt = stage.eta_tt;

            % Defines an output total pressure from total-to-total eff.
            p_func = @(t_ratio, p_start, eta_tt, kappa) ...
                    p_start * ((1 + (1/eta_tt)*...
                    (t_ratio - 1))^(kappa/(kappa-1)));

            % Iteratively Solving for the Outflow Total Pressure
            % Access to stages prop. is avoided since this takes too long
            T = linspace(T0_in, T0_out, obj.N+1);
            for i = 1:obj.N
                t_ratio = T(i+1)/T(i);
                p_end = p_func(t_ratio, p_start, eta_tt, obj.inflow.kappa);
                p_start = p_end; % Setting start
            end

            % Calculated Polytropic Efficiency
            kappa = obj.inflow.kappa;
            eta_calc = (kappa / (kappa-1)) * (log(T0_out/T0_in) ...
                    / log(p_end/obj.inflow.p0));
            residual = eta_p_hat - eta_calc;
        end
        
        function obj = calcPolytropic(obj)
            tic;
            options = optimoptions('lsqnonlin','Display','iter');
            x = lsqnonlin(@obj.objective, 0.9, 0, 1, options);
            disp(x);
            obj.eta_p = x;
            obj.converged = true;
            t = toc;
            fprintf('Polytropic Eff. Solver Took:  %0.3f [s]', t)
        end
        
        function obj = buildStages(obj)
            if obj.converged
                if ~obj.mach_known
                    stage = definitions.Stage(obj.inflow, obj.omega,...
                                              obj.psi, obj.phi, obj.R,...
                                              obj.w);
                    obj.inflow = obj.inflow.update_state('V', stage.c_1);
                    obj.mach_known = true;
                end
                stg_cell = cell(obj.N,0);
                for i=1:obj.N
                    if i==1
                        in = obj.inflow;
                    else
                        in = stg_cell{i-1, 1}.outflow;
                    end
                    stage = definitions.Stage(in, obj.omega, obj.psi,...
                                              obj.phi, obj.R, obj.w,...
                                              'index', i);
                    stg_cell{i, 1} = stage;
                end
                obj.stages = stg_cell;
                obj.stages_complete = true;
            else
                obj = {};
            end
        end
    end
end

