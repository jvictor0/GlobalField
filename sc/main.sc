
Server.default.waitForBoot({
	var base_timestamp;
	var base_clock;
	
	"booted".postln;
	OSCFunc( { | msg, time, addr, port |
		("recv " + msg[1]).postln;
		("scheduling at " + (msg[1].asFloat - base_timestamp + base_clock).asString).postln;
		SystemClock.schedAbs(msg[1].asFloat - base_timestamp + base_clock,
			{ |t| "do".postln; Synth(msg[2]) });
	}, "/gf_play" );

	OSCFunc( { | msg, time, addr, port |
		("base timestamp " + msg[1]).postln;
		base_timestamp = msg[1].asFloat;
		base_clock = SystemClock.seconds;
	}, "/gf_start_clock" );

	SynthDef(\tik, { OffsetOut.ar(0, Impulse.ar(0)); FreeSelf.kr(Impulse.kr(0)); }).add;
});

