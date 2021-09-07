// from https://www.local-guru.net/blog/2018/2/10/SuperCollider-drumsample-generator
//

SynthDef.new("guru_blog_bd", {
    arg  n=0.8, nl = 0.02, start=110, end=1, l1=0.1, l2=0.3, exp=1.7;
    var boom;
    e = pow(Line.ar(0.9,0,l2),exp);

    boom = BBandPass.ar(WhiteNoise.ar(),freq:Line.ar(100,10,nl))*Line.ar(1,0,nl)*n+
    SinOsc.ar(Line.ar(start, end, l1))*e;
    Out.ar(0,[boom,boom])

}).add;

SynthDef.new("guru_blog_clap", {
    arg delay = #[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], rel=0.1, freq=600;

    var osc = Mix.arFill(10, { arg i;
        PinkNoise.ar()*0.3*EnvGen.ar(Env([0,0,1,0],[delay[i], 0.001, rel]), curve: \exp , doneAction: 0);
    });

    var snd =  BHiPass.ar(osc,freq);
    Out.ar(0,Pan2.ar(snd))
}).add;

SynthDef.new("guru_blog_crash", {
    arg freq = #[1600,200,199,388,785, 2784, 100,177,1384,1730,1255,1160], rel=0.6, noiseRel=0.01, noiseLevel=0.7;

    var osc = Mix.arFill(12, { arg i;
        Pulse.ar(freq[i])*0.3;
    });
    var e = EnvGen.ar(Env.perc(0.01, rel));

    var noiseOsc = PinkNoise.ar();
    var noiseEnv = EnvGen.ar(Env.perc(0.01, noiseRel))*noiseLevel;

    var snd =  noiseOsc * noiseEnv + BHiPass4.ar(osc,1000)*e;
    Out.ar(0,Pan2.ar(snd))
}).add;

SynthDef.new("guru_blog_ding", {
    arg freq = #[1600,200,177,384,730,1255,60], rel=0.1, noiseRel=0.01, noiseLevel=0.7;

    var osc = Mix.arFill(7, { arg i;
        SinOsc.ar(freq[i])*0.3;
    });
    var e = EnvGen.ar(Env.perc(0.01, rel));

    var noiseOsc = PinkNoise.ar();
    var noiseEnv = EnvGen.ar(Env.perc(0.01, noiseRel))*noiseLevel;

    var snd =  noiseOsc * noiseEnv + osc*e;
    Out.ar(0,Pan2.ar(snd))
}).add;

SynthDef("guru_blog_hh", {
    arg noiseRel = 0.4, noiseLevel=0.7, ffreq=10000, q=0.2;
    var noiseOsc = BBandPass.ar(PinkNoise.ar(), ffreq, q);
    var noiseEnv = EnvGen.ar(Env.perc(0.01, noiseRel));
    var snd = noiseOsc * noiseEnv * 1.4;
    Out.ar(0,Pan2.ar(snd, 0, 1));
}).add;

SynthDef("guru_blog_sn", {
    arg startPitch = 6000, endPitch=60, clickLevel=0.7, pitchRel = 0.11, noiseLevel=1, noiseRel= 0.3;
    var pitchEnv = EnvGen.ar(Env([startPitch,410,endPitch],[0.005,0.01], curve:\exp));
    var clickOsc = SinOsc.ar(pitchEnv);
    var clickEnv = EnvGen.ar(Env.perc(0.001, pitchRel))*clickLevel;
    var noiseOsc = PinkNoise.ar();
    var noiseEnv = EnvGen.ar(Env.perc(0.01, noiseRel))*noiseLevel;
    var snd = clickOsc *clickEnv + noiseOsc * noiseEnv;
    Out.ar(0,Pan2.ar(snd, 0, 1));
}).add;

SynthDef("guru_blog_tom", {
    arg startPitch = 6000, endPitch=60, clickLevel=0.7, pitchRel = 0.11, noiseLevel=1, noiseRel= 0.3;
    var pitchEnv = EnvGen.ar(Env.perc(0.01, pitchRel));

    var clickOsc = SinOsc.ar(pitchEnv*(startPitch-endPitch)+endPitch);
    var clickEnv = EnvGen.ar(Env.perc(0.001, pitchRel))*clickLevel;
    var noiseOsc = PinkNoise.ar();
    var noiseEnv = EnvGen.ar(Env.perc(0.01, noiseRel))*noiseLevel;
    var snd =  noiseOsc * noiseEnv +clickOsc *clickEnv;
    Out.ar(0,Pan2.ar(snd, 0, 1));
}).add;