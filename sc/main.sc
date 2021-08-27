
Server.default.waitForBoot({
	var base_timestamp;
	var base_clock;
	
	"booted".postln;
	OSCFunc( { | msg, time, addr, port |
		var args = Array.new(msg.size - 3);
		msg.postln;
		(msg.size - 3).do({ | i |
			if(i % 2 == 1, {args.add(msg[i + 3].asFloat)}, {args.add(msg[i + 3])});
		});
		SystemClock.schedAbs(msg[1].asFloat - base_timestamp + base_clock,
			{ |t| Synth(msg[2], args) });
	}, "/gf_play" );

	OSCFunc( { | msg, time, addr, port |
		("base timestamp " + msg[1]).postln;
		base_timestamp = msg[1].asFloat;
		base_clock = SystemClock.seconds;
	}, "/gf_start_clock" );

	SynthDef(\tik, { |freq| OffsetOut.ar(0, Impulse.ar(freq)); FreeSelf.kr(Impulse.kr(0)); }).add;
});

