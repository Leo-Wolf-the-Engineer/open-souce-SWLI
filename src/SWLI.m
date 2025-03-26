%% 
clc,clear,close all
format short

%% Set video parameters
fps = 90; %frames per second
vel = 0.75; %scan speed, micron per second

lambda_m = .5; %mean wavelength of source 
filename = "capprobeBBS_90fps_750nmps.AVI"; %data file name

savefile = 0; %save output as TIFF?
outputfilename = 'capprobeBBS_lowpassandenv.tif'; %TIFF file name


%% load video
muperframe = vel/fps %microns moved per frame

    disp("Vid loading")
    tic
    v = VideoReader(filename);
    i = 1;
    length = v.NumFrames();
    while i<=length %hasFrame(v)
        frames(:,:,i) = single(rgb2gray(readFrame(v))); 
        i=i+1;
    end
    frameindex = [1:1:length];
    tempposition = linspace(0,length*muperframe,length);
    toc

%display sample frame for no reason
frame = frames(:,:,50);
figure(1)
s = surf(frame);
s.EdgeColor = 'none';

i = 1;
k = 1;
output = zeros(v.Height,v.Width);
length = v.NumFrames(); 
frameindex = [1:1:length];
%% playing with a fourier based demodulation technique, ignore

%prepare frequency analysis tools
carrier_period = lambda_m/muperframe/2;
M = exp(-1.0j*2*pi*frameindex/carrier_period);% Demodulation sinusoid
%M = sin(2*pi*frameindex/carrier_period);
%cutoff = ceil(length/carrier_period);
cutoff = 12;

pixtimevector = squeeze(frames(200,300,:))';
pixtimevector = pixtimevector-mean(pixtimevector);
%notch filter test 
FD = fft(pixtimevector); %25 %47
lc = 25;
hc = 47; 
FD(1:lc) = 0;
FD(hc:end-hc) = 0;
FD(end-lc:end) = 0;
notched = ifft(FD);

%FFT env test
demod = M.*pixtimevector;
FDdemod = fft(demod);
FDdemod(cutoff:end-cutoff)=0;
env = 2*abs(ifft(FDdemod));

figure(10)
hold on
plot(real(M))
plot(pixtimevector)
plot(env)
plot(real(notched))
hold off
figure(11)
plot(abs(FD(1:100)))
figure(12)
plot(abs(FDdemod(1:100)))
%% Perform the actual analysis
k = 1;
tic
while k<v.Width
    i = 1;
    while i<=v.Height

        pixtimevector = squeeze(frames(i,k,:))';
        %pixdisp = tempposition(I);
        %envmidline = sum(frameindex.*env) / sum(env);
        pixtimevector = (pixtimevector-mean(pixtimevector)).^2; %center about zero then square
        %env = envelope(pixtimevector,1000);
        %env = envelope(pixtimevector,30,"peak");
        %env = envelope(pixtimevector,500);
        %envmidline = sum(frameindex.*env) / sum(env);
        envmidline = sum(frameindex.*pixtimevector) / sum(pixtimevector); %calc centroid of signal
        %[~,I] = max(pixtimevector);
        pixdisp = envmidline*muperframe;

        output(i,k) = -pixdisp;

        i=i+1;
    end
    k = k+1;
end

toc
output = output(:,1:end-1,:);
output = output-mean(mean(output));
%output = lowpass(output, .5);
figure(2)
s = surf(output);
s.EdgeColor = 'none';


%% OUTPUT AS TIFF
if savefile == 1
    output = single(output);

    fileName = outputfilename;
    tiffObject = Tiff(fileName, 'w');
    % Set tags.
    tagstruct.ImageLength = size(output,1); 
    tagstruct.ImageWidth = size(output,2);
    tagstruct.Compression = Tiff.Compression.None;
    tagstruct.SampleFormat = Tiff.SampleFormat.IEEEFP;
    tagstruct.Photometric = Tiff.Photometric.MinIsBlack;
    tagstruct.BitsPerSample = 32;
    tagstruct.SamplesPerPixel = size(output,3);
    tagstruct.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky; 
    tiffObject.setTag(tagstruct);
    % Write the array to disk.
    tiffObject.write(output);
    tiffObject.close;
    % Recall image.
    m2 = imread(fileName);
    % Check that it's the same as what we wrote out.
    maxDiff = max(max(m2-output)) % Should be zero.
end 


%% another random playground to see what adjacent pixels' signals look like and play with different enveloping methods 

i = 351; k = 165;
tic
pixtimevector = [frames(i,k,:)];
pixtimevector = reshape(pixtimevector, 1, length);

%[upenv,loenv] = envelope(pixtimevector,150);
pixtimevector = pixtimevector-mean(pixtimevector);
pixtimevector = lowpass(pixtimevector,0.025); %pi*rad/sample
%[M,I] = max(pixtimevector);
% pixtimevector = (pixtimevector-mean(pixtimevector)).^2;
        env = envelope(pixtimevector,500);
        envmidline = sum(frameindex.*pixtimevector) / sum(pixtimevector);
toc
disp(envmidline*muperframe)

figure(3)
tiledlayout(2,2);
nexttile;
hold on
plot(frameindex,pixtimevector)
%plot(envmidline*[1,1], ylim(gca), 'g', 'LineWidth', 3.0);
plot(env)
hold off

tic
pixtimevector = [frames(i+1,k,:)];
pixtimevector = reshape(pixtimevector, 1, length);
[upenv,loenv] = envelope(pixtimevector,150);
envmidline = sum(frameindex.*upenv) / sum(upenv);
toc
[M,I] = max(upenv);
pixdisp = tempposition(I)
disp(envmidline*muperframe)
nexttile;
hold on
plot(frameindex,pixtimevector, frameindex, upenv, frameindex, loenv)
plot(envmidline*[1,1], ylim(gca), 'g', 'LineWidth', 3.0);
hold off

pixtimevector = [frames(i,k-1,:)];
pixtimevector = reshape(pixtimevector, 1, length);
[upenv,loenv] = envelope(pixtimevector,150);
envmidline = sum(frameindex.*upenv) / sum(upenv);
[M,I] = max(upenv);
pixdisp = tempposition(I)
disp(envmidline*muperframe)
nexttile;
hold on
plot(frameindex,pixtimevector, frameindex, upenv, frameindex, loenv)
plot(envmidline*[1,1], ylim(gca), 'g', 'LineWidth', 3.0);
hold off

pixtimevector = [frames(i+1,k-1,:)];
pixtimevector = reshape(pixtimevector, 1, length);
[upenv,loenv] = envelope(pixtimevector,150);
envmidline = sum(frameindex.*upenv) / sum(upenv);
[M,I] = max(upenv);
pixdisp = tempposition(I)
disp(envmidline*muperframe)
nexttile;
hold on
plot(frameindex,pixtimevector, frameindex, upenv, frameindex, loenv)
plot(envmidline*[1,1], ylim(gca), 'g', 'LineWidth', 3.0);
hold off


i = 250; k = 250;
pixtimevector = [frames(i,k,:)];
pixtimevector = reshape(pixtimevector, 1, length);
[upenv,loenv] = envelope(pixtimevector,150);
envmidline = sum(frameindex.*upenv) / sum(upenv);
[M,I] = max(upenv);
pixdisp = tempposition(I)
disp(envmidline*muperframe)



figure(4)
k = 342; i = 428;
hold on
pixtimevector = squeeze(frames(i,k,:));
plot(pixtimevector)
pixtimevector = squeeze(frames(i+1,k,:));
plot(pixtimevector)
pixtimevector = squeeze(frames(i+1,k+1,:));
plot(pixtimevector)
pixtimevector = squeeze(frames(i,k+1,:));
plot(pixtimevector)



pixtimevector = reshape(pixtimevector, 1, length);


pixtimevector = pixtimevector-mean(pixtimevector);
FD = fft(pixtimevector);
figure(5)
tiledlayout(1,3)
nexttile()
plot(pixtimevector)
title("Signal")
nexttile()
plot(abs(FD(1:140)))
title("Cropped Fourier magnitude")
nexttile()
plot(angle(FD(1:140)))
title("Cropped Fourier phase")

