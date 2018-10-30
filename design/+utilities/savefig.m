function savefig(fig_h)
%SAVEFIG Formats figure and saves as pdf

%     AR=[8 5]; %Aspect Ratio
%     Margin=0.15; %Control Figure Margins
%     NF=0.02; %Distance to Nudge Plot to Compensate for Axis Labels
    
    if isa(fig_h, 'matlab.ui.Figure')
        name = fig_h.Name;
        
        % Formatting Axis Position
        axis = get(fig_h,'CurrentAxes');
        pbaspect(axis, [2 1 1])
        set(axis,... %Formatting Alignment
            'color', [0.95 0.95 0.95]);

        set(fig_h, 'InvertHardCopy', 'off');
        set(fig_h, 'color', [1, 1, 1])
        
        fig_h.PaperPositionMode = 'auto';
        fig_pos = fig_h.PaperPosition;
        fig_h.PaperSize = [fig_pos(3) fig_pos(4)];

        % Formatting Axis Position
        axis = get(fig_h,'CurrentAxes');
        pbaspect(axis, [1.5 1 1])
        set(axis,... %Formatting Alignment
            'color', [0.95 0.95 0.95],...
            'FontSize',8,...
            'TickLabelInterpreter','LaTex');
        
        % Saving Figure
        saveas(fig_h, [pwd '\Figures\' name] , 'pdf')
        
    else
        % FIXME implement method to save multiple figures
        error('Not yet implemented')
    %     for fig = figure_handle
    %     end
    end
end

