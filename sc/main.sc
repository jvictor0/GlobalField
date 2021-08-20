
Server.default.waitForBoot({
	var fnc;
	"booted".postln;
	fnc = OSCFunc( { | msg, time, addr, port |
		"recv".postln;
		Synth(msg[1])
	}, "/gf_play" );

	SynthDef(\tik, { OffsetOut.ar(0, Impulse.ar(0)); FreeSelf.kr(Impulse.kr(0)); }).add;
});

