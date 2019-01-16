classdef DesignVector < dynamicprops
    %DESIGNVECTOR Utility class allowing key, value pairs
    %   Solves the hassle of having to remember indices w/ fmincon

    properties
        init                % Initial Values of the Design Vector
        vector              % Current Design Vector
    end
    
    properties (SetAccess = private, GetAccess = private)
        keys                % Design Vector Keys
        cell                % Input cell containing key, value pairs
    end
    
    properties (SetAccess = private)
        lb                  % Lower Bounds of Design Variable
        ub                  % Upper Bound of Design Variable
    end
    
    methods
        
%     function obj = DesignVector(psi, phi, R, N)
%         obj.psi = psi; obj.phi = phi; obj.R = R; obj.N = N;
%         obj.vector = [psi, phi, R, N];
%     end

        function obj = DesignVector(cell)
            
            obj.cell = cell;

            obj.init = cell2mat(cell(:,2));
            obj.vector = ones(length(obj.init));
            obj.keys = cell(:,1);
            obj.lb = cell2mat(cell(:,3));
            obj.ub = cell2mat(cell(:,4));
            
            index = 1;
            for key = obj.keys'
                P = addprop(obj, key{:});
                P.GetMethod = @(getter) obj.vector(index) * ...
                                         obj.init(index);
                index = index + 1;
            end
        end

    %  function obj = DesignVector(data, keys)
    %      if nargin == 0
    %         data = 0;
    %         keys = '';
    %      elseif nargin == 1
    %         keys = '';
    %      end
    %      obj = obj@double(data);
    %      obj.keys = keys;
    %   end
   
%       function sref = subsref(obj,s)
%         switch s(1).type
%            case '.'
%               switch s(1).subs
%                  case 'keys'
%                     sref = obj.keys;
%                  case 'Data'
%                     d = double(obj);
%                     if length(s)<2
%                        sref = d;
%                     elseif length(s)>1 && strcmp(s(2).type,'()')
%                        sref = subsref(d,s(2:end));
%                     end
%                  otherwise
%                     error('Not a supported indexing expression')
%               end
%            case '()'
%               d = double(obj);
%               newd = subsref(d,s(1:end));
%               sref = definitions.DesignVector(newd,obj.keys);
%            case '{}'
%               error('Not a supported indexing expression')
%         end
%      end
     
%      function obj = subsasgn(obj,s,b)
%         switch s(1).type
%            case '.'
%               switch s(1).subs
%                  case 'keys'
%                     obj.keys = b;
%                  case 'Data'
%                     if length(s)<2
%                        obj = definitions.DesignVector(b,obj.keys);
%                     elseif length(s)>1 && strcmp(s(2).type,'()')
%                        d = double(obj);
%                        newd = subsasgn(d,s(2:end),b);
%                        obj = definitions.DesignVector(newd,obj.keys);
%                     end
%                  otherwise
%                     error('Not a supported indexing expression')
%               end
%            case '()'
%               d = double(obj);
%               newd = subsasgn(d,s(1),b);
%               obj = definitions.DesignVector(newd,obj.keys);
%            case '{}'
%               error('Not a supported indexing expression')
%         end
%      end
     
%      function newobj = horzcat(varargin)
%         d1 = cellfun(@double,varargin,'UniformOutput',false );
%         data = horzcat(d1{:});
%         str = horzcat(cellfun(@char,varargin,'UniformOutput',false));
%         newobj = definitions.DesignVector(data,str);
%      end
     
%      function newobj = vertcat(varargin)
%         d1 = cellfun(@double,varargin,'UniformOutput',false );
%         data = vertcat(d1{:});
%         str = vertcat(cellfun(@char,varargin,'UniformOutput',false));
%         newobj = definitions.DesignVector(data,str);
%      end
     
%      function str = char(obj)
%         str = obj.keys;
%      end
     
%      function disp(obj)
%         disp(obj.keys)
%         disp(double(obj))
%      end
  end
end
