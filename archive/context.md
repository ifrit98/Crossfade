You know, like of bo- of both problems and the common physics between them, uh, 

that, that would be the ultimate. [chuckles] 

Right. 

Because then you know it would generalize across everything. 

So I, I was kind of hoping- 

You know, everything waves related. [chuckles] 

E-exactly, and I think this set of powerful abstractions is, like, kind of what drove us talking about the physics-based neural networks or physics-informed neural networks, and, like, how that literature has developed in the last couple of years, I think makes what we're talking about a lot more feasible. And it's not just like, "Hey, throw an LLM at this." It's, "Here's an inte- a way to integrate multiple systems with multiple domain-specific models," whether they're physics-based, direct, you know, math, or whether they're ML models that have been t- trained on specific domains, and then putting all that together so that then you can notice correlations across the domains and then maybe, 

hopefully train models that 

basically target the Venn diagram of all those features. And then that's really the secret sauce, is getting us across, uh, you know, like, okay, well, what are the things that we care about for sonar, for a torpedo, whether it's coming at you or moving away from you, or any fast object, um, 

how can we get that to translate across to OTH or to radar or, you know, some, like, 

RF stuff? 

Or UAS. [chuckles] Yeah. 

C-UAS, right. So I think Tim's really interested in the CO- UAS side. I think he's really interested in command and control. I think expanding kind of Ninja is, in his mind, I think, the foot in the door to say like, "Well, now we can add all these, like, AI capabilities to already assist our operators." But I feel like that's, that's almost, like, so low-hanging fruit. It's just to, like, 

get buy-in rather than- 

Yeah 

... here's the real- 

Yeah 

... leverage that we can apply, which I'm- 

It's to get money too, right? Like, or funding to, to build out our, you know, cr- our charge code 'cause there's a lot more charge code dollars out there for, for Ninja and adding onto it and ju- easy, easy to justify, right, for Tim and to, you know, to anyone- 

Yes 

... versus, like, for Matt, it's, like, a little bit more specific. I, I, I mean, he... 

Uh, we do what we want kind of anyway, but... [chuckles] 

Right. But I think Tim is very aligned. I, I think I was encouraged by having... I probably had, like, a two-hour chat with him, and he's 

probably more on board than he lets on. I think he's very excited about 

what we can do with AI tooling, not just internally, but then expanding the scope of business and improving what we already have. So I think he's thinking- 

Yeah 

... multi-dimensionally, which is good. But I also think he's, like you're saying, I think thinking reasonably about, "Well, how do I get contract dollars? How do I get developer time paid for? How do I get not only, like, buy-in from the C-suite, but also on the government side?" So I think- 

Yeah 

... he's thinking, like... He's thinking chess. You know, he's playing chess, and I think that's great. I think he's got the right attitude. He's- 

That's his new job [laughs] basically. 

Right. 

So what I wanted to do was have a follow-up with him where we could talk a little bit more technically about that, uh, and particularly about the domain generalization piece, not so much the, like, operator synthesis side. So, uh, I was hoping that you and I, just before we have a call with Tim, 

e-even just more for me, because I think... I, I still think that you have a more, uh, 

deep intuition about how these things will translate. 

I work in a lot of data. [chuckles] There's a lot of different kinds of data. 

Right. So- 

Yeah 

... would it be okay if we spent a few minutes just if you could, like, lay out, "Here's what I see. Here are the things that made the bells go off for me, and what do you think that 

the system would, would do or would look like based on your intuitions?" 

Yeah. Um, so 

I guess generally speaking, right, like, a little background, right, I mainly work HF radar programs and, right, these sonar programs. Done a lot, you know, basically a lot of work in those two domains where it's all wave propagation. It's all... If you wanna do the modeling, it's not... It... Nothing is nice, uh, point-to-point. You know, nothing im- is like a mirror reflective ray tracing. Everything is bending. All the channels are dispersive. The te- the sound speed profile or the ionosphere, you know, the plasma density ionosphere changes, the sound speed profile changes. 

Hmm. 

It all screws with... It's honestly amazing that radars under... or, you know, radar and, you know, HF radar and sonars actually work or, like, you can actually detect stuff with them in some ways. Like, propagation's so complicated. Um, in some ways, like, the idea of 

the ionosphere is like if you were to take the ocean and flip it on its head, right, or basically take the one and flip it over, they're analog- analogous to, like, right, you get a good bottom reflection in, in the water, but you get an ionospheric reflection in HF radar. And there's a lot of, like, you know, as we're doing stuff with TVAPM on- 

... trace and front row, I'm doing the same exact things kind of on the HF radar programs, right, with ray tracers. And it's all bending rays, and it's all kind of the same, uh, same ray homing, ray tracing. That's what it takes to model the propagation from point A to point B. And that all generalizes across, 

you know, that generalizes to RF, you know, all the different bands. It's in the whole, the whole rainbow, the whole spectrum, um, technically, right? Like, there are different intricacies, right? Different 

words people use to describe them, but the physics is kind of all the same. It's all propagation of waves, and some of the same waveforms are used if it's an active system, that kind of thing. Uh, 

and so, like, what, what really, like, the, what spurred the idea kind of was some of this cepstral processing or this idea of the blind, 

uh, signal agnostic channel estimation. 

Because really, 

channel estimation, like when you're... Let's say even if you have a, like a backscatter radar, a radar that's actively transmitting and receiving an array, whatever, right? And there's an aircraft out there you're trying to detect. It... 

Ultimately, when you're looking at the displays, like a range-Doppler map or, or whatever, you're ultimately looking at some representation of the, of, uh, or measurement of the channel's response, like the propagation channel. 

Hmm. 

Right? It's either one way, maybe between in an underwater or the passive trace problem is one way between the, the torpedo making this noise to, to the receiver. But in, in, in radar, right, in, in radar it's bou- you know, bouncing off, right, or being backscattered. Uh, so it's, that's a two-way propagation, so there's two propagation lengths to worry about. 

Mm-hmm. 

But ultimately, in both cases, the 

channel response is really what you care about, and that inherently has the things that tell you if the target's there. 

Um- 

And that's inherently a topology. Like, you're interested in- 

Yeah 

... what is the topology of the reflecting surfaces. 

Yeah. Yeah. It, it's, that, that's basically the problem in both domains. And in RF, right, like if, if you're talking about a comm system, 

to do a good job of decoding a signal, again, it's that same problem of can you use the signal to, to estimate the, you know, like basically use the pilots and the carrier tones and things like that to estimate the channel between the source and the receiver so that you can equalize it out and then do a good job decoding the actual data packets, right? Um, so again, it, it's like this common thread of the, uh, channel 

propagate, you know, basically the propagation channel across all three of those domains. 

Um, 

and so I gue- I guess that's, that's why it's super interesting to me, like the, like, the, the cepstral stuff is 'cause it's like a blind thing. Audrey's been doing stuff with trying to get it to work in Ninja. 

Uh, the, the problem in Ninja is that it's a lot of signals that are all pent up in the same band. 

Hmm. 

And so it's like you get the superposition of all these different signals and traces, and they're all highly overlapped, right? 

Hmm. So disentangling- 

So it, it's an association problem of I see these traces, these multipath traces, or they're, they're there because the physics say they have to be, right? They're reflections in RF. Um, but they're all, like, 

you know, bound up together, and it becomes like a, an association problem. You might see the, the multimode trace, but you might see one or two or three multimode traces, but you don't, don't have any idea which source it's associated with. And there are things you could do. There's blind source se- separation techniques and things like... I mean, I'm going off the, the, going down the road of talking about more, like, signal processing-esque things, but it's kind of motivating or thinking about, like, what, you know, if, what, what, what the AI might be looking for across these domains, 

uh, or what, what it might recognize or what might be the common thread that, like, if we could get it to learn and look for that. 

Mm-hmm. 

In, in spectrograms, right, like, uh, like at, at RF, like, it, it's like we, we... All the displays are the same too. It's like a time frequency display is what we look at, uh, you know, people look at for Ninja, like a spectrogram. That's a very common, you know, if you are doing a detection, if you don't have knowledge of the signal, oftentimes you're looking at time frequency. And that's what we're looking at, beam time series and beam, you know, beam level spectrograms. That's exactly what we're looking at for trace. Uh, there's a lot of information there, especially about, like, just is something there or not. You know, like, is... Because an operator could spot like, "Oh, I see this, uh, red hot signal jumping around in frequency." Um, 

so I don't... That, uh- 

So it's like an association problem from a common representation. I think that's... Like, when I think of ML- 

Yes 

... and, and what it would leverage the most would be 

can, can I get... And I think it's the same problem for mathematics in general. Like, can, can I transpose a problem I already... Uh, sorry, can I transpose a new problem into a form that I already have solutions for, for other problems? So I think with- 

Yes 

... with this- Are spectrograms or s- or time frequency spectral representations as a broad class this shared representation? Would you say that it's fair to say we could... Even if they're not all aligned, like even if the axes are different and maybe they're on different scales, maybe one's log and one's linear, maybe they're in different bands, but, like, the same type of, let's call it a gram. Uh, do you think it's fair to say that we could get things on some kind of level playing field with this model? 

Potentially, yeah. I mean, 

it... Yeah, I mean, it'd be... Yeah, of course, everything's limited by, like, your sample rate and, like, you know, what, what's your resolution? What... You know, what's the Rayleigh resolution? What's your sample rate? 

Mm-hmm. 

What are... What's the, what's the chunk length or how, how long are your windows to generate your spectrograms? All of that. But in some ways, I don't know, like, 

all of that, all... It seems like a lot of the signal processing and engineering that we do is fighting, like, fixed gridded representations of things, like images, right? Like pixels, right? We're, we're using these discrete things, right? 'Cause that's what we can put on a display is, like, discrete things. But in reality, it's just sampling this continuous or more continuous space. 

And in, in some ways, like, thinking that, that, that's even more meta or, like, going even crazier out on the... Like, if, if we could get AI to do something like thinking in... or, or, or take a sampled signal, you know, something that's sampled and then consider it in a more, you know, 

continuous manifold or, or whatever. 

Well- 

Right? Because in theory, the, the... if, 

if those samples contain the information 

in some... You know, maybe it's hard to see. Maybe you can't see it at all visibly in whatever domain it's in- 

Mm-hmm. 

... but it contains the information. 

Uh, you know, I don't know. Like, that, that ends up becoming, like, the practical engineering problem is, well, what do I set my, my time windows for my FFTs lengths and all that stuff? Like, that's a practical problem of, well, how do I do HF radar versus how do I do sonar, which is at, you know, completely different signal band with completely different frequencies. Um, that, that's kind of like the, the practical engineering problem. 

Mm-hmm. 

But I don't know if, if ML could somehow solve that, or AI could somehow solve that or, like- 

Mm-hmm. 

... interpret something 

in the right way. 

Right, 'cause I think it will be some kind of combination of domain expertise to, to guide the tuning, to get to a common representation across these domains. So if- 

Yes. 

You know, like, I'm just thinking for sonar with trace, whether it's a spectrogram or a cepstrum or some kind of spectral processing. Okay, 

we have that tuned specifically for, you know, the kind of environment and the, like, reflective surfaces that are common, like the bathymetries that you're gonna see. But that's- 

Yeah. 

... gonna... Those channel effects are gonna defer from the channel effects from an over-the-horizon radar, 

but, like, if you're bouncing off the ionosphere. But at the same time, really, we wanna subtract those two things off. Like, we wanna get to- 

Yeah, we wanna factor them out. [chuckles] 

Exactly. 

And then get it into the same latent space, right? That's kind of the idea. Or I don't know if it'd be... You know, it's not necessarily a VAE, but- 

Right. 

... kind of that... Some, some representation space. 

Right. And I think then the question, the, like, ML training question becomes, what training setup? Like, what goal and what, [lip smack] um, uh, what thing are you either classifying or trying to reproduce that aligns all of these spaces naturally without having to, like, carve something up and say, "I'm gonna enforce this section as this type of, you know, physics, subset of physics, and this, this section- 

Yeah. 

... is something different." 

But I kind of think it might be, like, impulse responses of channels. 

Hmm. 

Right? Because that, that's kind of, like, what ties them together is, like... And, and the timescales might be different, right? Obviously, speed of light is different than the speed of sound, right? [chuckles] 

Mm-hmm. Mm-hmm. 

But, like, ultimately, in my mind, right, like, the, the impulse response function of the channel or the scattering function of the channel, 

these channels are kind of... 

That's what, at least from the physics side, or at least the way I wrap around, wrap my head around the physics of what's going on and how I interpret it, and how you can model a channel in both domains is kind of from, like, a scattering function or an impulse- 

Hmm. 

... you know, time-varying impulse response function type of- 

So is there a- 

Right. 

And I don't know if we have the answer, but just, like, broadly, is there a, um, 

a way to learn broad impulse response functions that will kind of generalize to a domain? So, like, even if you're in different bathymetries, can we have a broad, like, "Okay, here's what an impulse response will look generally like in an underwater or a sonar environment"? But, 

you know, I guess what I don't understand is how much detail, um, in the bathymetry profile affects that impulse response that would make it, um, not generalize cleanly.

There's a lot of distortion in both cases. Like, that's why it's a problem. [chuckles] That's what's so hard about it, about, like, why sonar, passive sonar is like, uh, you know, it's like you're doing what? Uh, it's like extremely low SNRs with very complex propagation. Um, 

and, and that's why the goal ultimately is kind of can you estimate... Ultimately, if, if you can estimate the scatter function, you've won, because the scatter function or the time, time-varying impulse response function is what will tell you if the target's coming towards you or if it is a target or not, or, um, 

you know, I, 

I don't know if that answers your question exactly, but... 

Uh, it does. It's really helpful because of what I, I think from my kind of information gathering goal here is to really just try to understand what are the problems that have prevented this from getting solved, and then I think how does that relate to 

our, 

you know, discussion about generalizing, uh, cross-domain representations? 'Cause i- if there's a physics-based methodology to subtract out some of those differences, like in, in the- 

Yeah 

... impulse response, um, 

then, across domains, then I think it will be easier- 

So basically- 

... for ML to learn it. 

So like a domain-agnostic impulse response function. So basically, we need to 

take the ch- well, our channel response. So what we need to do is figure out 

something that we can do maybe on the front end, or like basically a domain that we can project or a domain that we can transform those 

potential impulse response functions to that could be common amongst... Is, is that what you're getting at then? And it wouldn't necessarily be... 

Would, would it be an ML-created mapping into that space, or would it be a, 

into that kind of uniform space that's the same for- 

Right 

... you know, generalizes across all these domains, or would it be we try and rely on the physics to get it, or, or maybe we come up with some new maths, some new transform to, to- 

Mm-hmm 

... to do that? 

So I'm imagining this would be a research problem for, for both, approaching it both ways. So I think we would wanna find 

as many physics tools, whether it's like transformations or some kind of processing that we could do that gets us closer or, uh, uh, at removing some of those, um, channel effects that would be co-founding. But then at the same time, I think there would be ways to experiment with can we get an ML-based solution to work towards this, like the time frequency axis for attention in the, the transformer attention paper with, uh, the physics-informed one. So I think- 

Yep 

... uh, axial attention, that's what it's called. So I think that, to me, is... That, that's what I think really got me thinking more about this, where I think if we could 

almost... I don't know if it's gonna be a meet halfway, but I think it would be some kind of both/and. I don't think there's a... Well- 

Yeah 

... 'cause it sounds like- 

In some ways, you need the one to sanity check the other. [chuckles] 

Yeah. Yes. So my, my hope is that we would be able to have, 

uh... I think it would look something like a literature survey, right? So we would go and see, like, what are people doing, uh, how, how much work has been done on this kind of common representation, uh, across domains, and then what are people doing in the ML world about it, um, if there's any pros- progress there. And then how does that fit in with maybe us picking two domains, like whether it's, you know, an RF, uh, based thing and, and then sonar, um, and trying to kind of co-map them, and I, I think almost as like a little pilot to just see if the domain representations can be generalized across and it makes sense and it- 

It's like a... 

The word that ki- I want, want to say is invariant. 

Yes. 

Like domain invariant- 

Yes 

... something. 

Well, so, like, to your point about, 

like, an impulse response, it's like I don't think we would need an, an impulse response that generalizes across all domains. We would want domain-specific impulse response envelopes that would kind of help you get the contour that... It's almost like subtracting off the mean of that whole domain, even though we know it's not really accurate because there's a lot of complexity baked into that domain. But that, is there, like, an overall contour that... Uh, I'm thinking about it like in a manifold topology sense. Like what- 

Yeah 

... 

what 

is the, the intersection in the Venn diagram of all these domain topologies? 

And then use that as an axis to s- to navigate between them. So you're not, I think, trying to isolate the perfect generalized latent space. You're just trying to find a way to co-map and s- and bind them as like in a spine, 

and then you're able to go off into those other domains to get more granularity, like some of the, you know, really complex, um- 

... channel effects for sonar, where you might not need all of that specificity encoded in the shared representation. You just need to know how to get there from the shared representation. 

Does that make sense? 

Yeah, it just needs to be... 

And it's kind of like a Fourier transform. It's the reconstruction idea. You need to be all the in- the information can't be lost. 

Yes. 

It's like an information theory, uh, I'm, I can't remember what the... There's like the Taylor's data processing, uh, theory where from information theory, Taylor's whatever, information- 

Mm-hmm 

... inequality, that you can't add information by processing. You could sure take it away, but- 

That's right 

... you can't add it. And we don't, we want to main- whatever it is, it has to maintain it, for sure. 

Um- 

We can't lose fidelity at any point. But I think we could- 

Yeah. 

I think this is where maybe, like, good enough is 

the, the, like, how do you give the ML a hook 

to find its way? So you don't have to over-specify, "Oh, here's the exact, you know, imp IR response for this domain," or, "Here are the exact specifications for all of the channel effects that you might see in this domain." 'Cause that would be, like- 

Mm-hmm 

... an uncountably enu- you know, enumeration problem. Um- 

Yes. 

But just, "Oh, here's a signal enough where, okay, I'm in this domain." [lip smack] Um, it, it, it kind of gets back to what we talked about before in ter- for, uh, Front Row and TRACE with using the, um, striation patterns on the spectrograms as a way to, 

uh, derive physics-based features. You know, like how fast is it going? 

Yeah. 

Is it coming toward me or is it going away? 

It's all driven by under the hood by this, the, the temporary impulse response, right? That's why the speeds are there. [chuckles] 

Yes. 

That's the cool part. Yes. 

So I think I- I'm connecting this to, like, everything that we've talked about across all of those, those projects, like from Front Row to TRACE to, to now, is, uh, 

basically 

putting all of that into a format that we can then have an ML ingest. And they're, they're all, it's all not one big model, but I'm assuming it will be a family of models that maybe there are domain experts that know how to process those particular domains, and maybe they're trained on particular IR, you know, responses, uh, and channel effects for that domain. But then the outputs of those models end up being interpretable, interpretable a- across domains that maybe will be consumed by an LLM that then can say, "Hey, I've got outputs from model A that's in sonar land, and I've got outputs from model B that's in radar land, and here are the common representations, and now I'm looking for correlations across." And maybe there's other downstream models that combine them and process them. So I, I see it as multi-stage, multi-tier, um, infrastructure. But then the LLM is the thing that allows you to translate across these representations rapidly in a way that's human-readable and digestible. And then you can go back and say, "Well, you know, I think..." It is almost like a human feedback research open question, where then we can, as operators, say, "Hey, um, 

I think that this response was good, this response was bad. You missed this. This is an incorrect, like, inference." But then that can be recorded as training data for our own LLM, whether it's like a, a small, uh, LoRA adapter, right? Like a low-rank adapter that is just fine-tuned on top of the model. Uh, and then that is applied, you know, in-house, and then we wrap it all up, and now you have this system with a bunch of different models for, let's just say two domains for simplicity. And then you've got some sort of interoperability layer that correlates the outputs of the bespoke systems and models. And then you have an LLM that's aggregating it and is trained on how to interpret this data. And then that's what you surface to the operator. Is that reasonable? Does that make sense- 

Yeah 

... to what we're talking about? 

I think so. I think so. Yeah, I mean, there obviously are, like, hard... There's some mountains to climb or hills to get through or figure out, right? But I think AI can help us along the way too. You know what I mean? Like, 

that's the other part, right? Like, we can, 

we can... We're not alone. It's not just you and me. We c- we have our friend Claude and we have our friend ChatGPT and our whatever, right? 

That's true. That's really true. 

If... 

Yeah. Or, or, and maybe, maybe we want to keep it on Kotos or on, uh, Pandora or whatever, right? Like, maybe we keep it in hou- I don't know. Maybe we don't. Um, but 

yeah, 

it's i- it would be interesting to have those, um, 

yeah, that, tho- that conversation, like figure out kind of this generalized thing. 

Right. So- 

The LoRA, the LoRA stuff I think is really cool. I was reading about that, like, the cracking open the LLMs. 

Yeah. 

In some ways, like, that would be awesome to do for TRACE, 

right? It's like, oh, well, we're... In some ways, it short-circuits, like, a lot of it. I mean, I don't, I don't know. Like, 

if, if it worked, right? That's, that's the other thing is I feel like 

right now, the CBIR, the VAE, it's like 

we can wrap our heads around exactly what's going on with that, or y- you know what I mean? Like- 

Yeah 

... the pieces of the puzzle are, it's clearer, it's interpretable, it's understandable. We know, 

you know, latent spaces and things like that. But- 

I know. I think so too 

... the LLMs are so powerful, like the VLMs, LLMs are so powerful that I don't, you know... I guess I don't know where to start. I haven't, I haven't thought... I'm assuming it's gotta be similar 

in nature to, like, there are layers and you can, you know, the data, it's obviously attention layers and things like that. Um- 

Right. 

I guess, like, what in, what makes it an LLM is still, you know, I don't know enough to know that, oh, this is the difference between an LLM and a VAE, you know? 

Right. 

Other than... [chuckles] 

Well, we can, we can go... I can kind of talk you through that sometime. I think she's, she's getting up. I'm hearing her, so I gotta, I gotta hop off. 

Okay. 

But, um, let's, uh, let's follow up in the next week or two and we can talk a little bit more, because I think this is good to, to just kind of refine it a little bit. And then we, when we talk to Tim, I think this is... 'Cause I just, I want him to get more excited. That's what I want. 

Yeah. Yeah. Get, get our pitch together. [chuckles] 

Basically, yeah. So anyway, I, I gotta run, but we'll, we'll, we'll talk soon, man. 

Okay. 

Okay. 

Yeah.
