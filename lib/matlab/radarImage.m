function h=radarImage(data, header,v, R0, varargin)
p=inputParser();
p.addParamValue('ifft', '', @ischar);
p.addParamValue('fft', '', @ischar);
p.addParamValue('average2D',  [40,4], @isnumeric);
%p.addParamValue('pulse',  0, @isnumeric);
p.parse(varargin{:});

if strcmp(p.Results.ifft,'range')
    fsample=290;
    freq=linspace(-fsample/2, fsample/2,size(data,2));
    data=fftshift(ifft(data,[], 2),2);
elseif strcmp(p.Results.ifft, 'azimuth')
    data=fftshift(ifft(data,[], 1),1);
elseif strcmp(p.Results.ifft, 'both')
    data.fftshift(ifft2(data));
end

if strcmp(p.Results.fft,'range')
    fsample=290;
    freq=linspace(-fsample/2, fsample/2,size(data,2));
    data=fftshift(fft(data,[], 2),2);
elseif strcmp(p.Results.fft, 'azimuth')
    data=fftshift(fft(data,[], 1),1);
elseif strcmp(p.Results.fft, 'both')
    data.fftshift(fft2(data));
end
if any(p.Results.average2D ~= [1,1])
    im=20*log10(average2D(abs(data),p.Results.average2D(1),p.Results.average2D(2)));
else
    im=20*log10(abs(data));
end
MaxV = max(max(im)); %Find Image Maximum Value
h=figure();
if strcmp(p.Results.fft,'range')
    imagesc(freq, 1:size(im,1), (fliplr(im)));
    xlabel('Range Freq (MHz)','fontsize',16)
else
    imagesc((fliplr(im)));xlabel('Range px','fontsize',16)
end
colormap gray;colorbar;
if ~isempty(header)
    title(['R0: ', num2str(R0), ' Max Value ', num2str(MaxV), ' Vel: ' num2str(v), ' BW: ' num2str(header.bandwidth)],'fontsize',14,'fontweight','bold');
else
    title(['R0: ', num2str(R0), ' Max Value ', num2str(MaxV), ' Vel: ' num2str(v)]);
end
% %title(['Polarization: ', polarization],'fontsize',14);
ylabel('Azimuth px','fontsize',16)
% %axis([80 5800 0 10000])
% shg
end
