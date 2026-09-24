import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio,
  Sparkles,
  HelpCircle,
  Compass,
  Shield,
  Truck,
  TrendingUp,
  AlertTriangle,
  RotateCcw,
  Square,
  Play,
} from 'lucide-react';
import { DashboardResponse, DemoState } from '../../types';

interface CabVoiceAssistantProps {
  dashboard: DashboardResponse | null;
  demoState: DemoState | null;
  onChooseTrajectory?: (scenarioId: string) => void;
  onViewModeChange?: (mode: 'CAB_HUD' | 'DETAILED') => void;
  currentViewMode?: 'CAB_HUD' | 'DETAILED';
}

export type AudioPriority = 'NORMAL' | 'HIGH' | 'CRITICAL';

const PRIORITY_LEVELS: Record<AudioPriority, number> = {
  NORMAL: 1,
  HIGH: 2,
  CRITICAL: 3,
};

// Web Audio API Radio Sound Synthesizer (100% offline, zero assets needed)
const playRadioSound = (type: 'PTT_ON' | 'PTT_OFF' | 'ALERT' | 'CONFIRM') => {
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    const now = ctx.currentTime;

    if (type === 'PTT_ON') {
      // In-cab radio mic open chirp (880Hz -> 1320Hz)
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.setValueAtTime(1320, now + 0.035);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
      osc.start(now);
      osc.stop(now + 0.08);
    } else if (type === 'PTT_OFF') {
      // Radio transmission end squelch click
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, now);
      gain.gain.setValueAtTime(0.09, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
      osc.start(now);
      osc.stop(now + 0.04);
    } else if (type === 'ALERT') {
      // Dual-tone high priority safety horn
      osc.type = 'square';
      osc.frequency.setValueAtTime(900, now);
      osc.frequency.setValueAtTime(700, now + 0.08);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      osc.start(now);
      osc.stop(now + 0.22);
    } else if (type === 'CONFIRM') {
      // Double positive confirmation chime
      osc.type = 'sine';
      osc.frequency.setValueAtTime(523.25, now);
      osc.frequency.setValueAtTime(659.25, now + 0.06);
      gain.gain.setValueAtTime(0.14, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
      osc.start(now);
      osc.stop(now + 0.18);
    }
  } catch {
    // Tolerant of browser autoplay restrictions
  }
};

export const CabVoiceAssistant: React.FC<CabVoiceAssistantProps> = ({
  dashboard,
  demoState,
  onChooseTrajectory,
  onViewModeChange,
  currentViewMode,
}) => {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [voiceAudioEnabled, setVoiceAudioEnabled] = useState<boolean>(true);
  const [autoAnnounceEnabled, setAutoAnnounceEnabled] = useState<boolean>(true);
  const [isPTTHeld, setIsPTTHeld] = useState<boolean>(false);
  const [transcript, setTranscript] = useState<string>('');
  const [lastResponse, setLastResponse] = useState<string>(
    'CAT Cab Radio Voice Companion active. Hold Spacebar or tap Push-to-Talk to query fleet, pacing, or safety without taking eyes off the bench.'
  );
  const [currentPriority, setCurrentPriority] = useState<AudioPriority>('NORMAL');
  const [speechSupported, setSpeechSupported] = useState<boolean>(true);

  const recognitionRef = useRef<any>(null);
  const prevStepRef = useRef<number>(demoState?.current_step || 1);
  const prevAttentionModeRef = useRef<string>(dashboard?.attention_mode || 'NORMAL');
  const activePriorityRef = useRef<AudioPriority>('NORMAL');
  const speechTimeoutRef = useRef<any>(null);

  // Stop active speech playback immediately
  const stopSpeaking = useCallback(() => {
    if (speechTimeoutRef.current) {
      clearTimeout(speechTimeoutRef.current);
      speechTimeoutRef.current = null;
    }
    try {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    } catch {}
    activePriorityRef.current = 'NORMAL';
    setCurrentPriority('NORMAL');
    setIsSpeaking(false);
    playRadioSound('PTT_OFF');
  }, []);

  // Text-to-Speech synthesis with Priority Preemption
  const speak = useCallback(
    (text: string, priority: AudioPriority = 'NORMAL', forceInterrupt: boolean = false) => {
      if (!voiceAudioEnabled || typeof window === 'undefined' || !('speechSynthesis' in window)) {
        return;
      }

      // Priority preemption check:
      // If speech is already active and this call is NOT forced, ensure lower priority doesn't step on higher priority
      const currentLevel = PRIORITY_LEVELS[activePriorityRef.current] || 1;
      const incomingLevel = PRIORITY_LEVELS[priority] || 1;

      if (!forceInterrupt && incomingLevel < currentLevel) {
        // Drop lower priority speech if critical safety alert is playing
        return;
      }

      // Clear any pending speak timeout
      if (speechTimeoutRef.current) {
        clearTimeout(speechTimeoutRef.current);
        speechTimeoutRef.current = null;
      }

      // Cancel previous speech immediately
      try {
        window.speechSynthesis.cancel();
      } catch {}

      // Play tactical audio cue
      if (priority === 'CRITICAL' || priority === 'HIGH') {
        playRadioSound('ALERT');
      } else {
        playRadioSound('CONFIRM');
      }

      activePriorityRef.current = priority;
      setCurrentPriority(priority);

      // Brief 25ms timeout allows Chromium speech buffer to cleanly flush cancel command
      speechTimeoutRef.current = setTimeout(() => {
        try {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 1.03; // Measured authoritative dispatch pace
          utterance.pitch = 0.95; // Warm, authoritative radio tone with depth

          utterance.onstart = () => {
            setIsSpeaking(true);
          };
          utterance.onend = () => {
            setIsSpeaking(false);
            activePriorityRef.current = 'NORMAL';
            setCurrentPriority('NORMAL');
            playRadioSound('PTT_OFF');
          };
          utterance.onerror = () => {
            setIsSpeaking(false);
            activePriorityRef.current = 'NORMAL';
            setCurrentPriority('NORMAL');
          };

          window.speechSynthesis.speak(utterance);
        } catch {
          setIsSpeaking(false);
          activePriorityRef.current = 'NORMAL';
          setCurrentPriority('NORMAL');
        }
      }, 25);
    },
    [voiceAudioEnabled]
  );

  // Replay last transmission
  const replayLastTransmission = useCallback(() => {
    if (lastResponse) {
      speak(lastResponse, activePriorityRef.current, true /* forceInterrupt */);
    }
  }, [lastResponse, speak]);

  // Intent Processing Engine with Priority Categorization
  const processQuery = useCallback(
    (query: string) => {
      const q = query.toLowerCase().trim();
      const twin = dashboard?.shift_twin_summary;
      const safety = dashboard?.immediate_safety_status;
      const isSafetyAlert =
        safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0;
      const isDecisionAlert =
        dashboard?.attention_mode === 'DECISION_FOCUS' || demoState?.decision_point;

      let answer = '';
      let priority: AudioPriority = 'NORMAL';

      // 1. Truck / Fleet Status
      if (
        q.includes('truck') ||
        q.includes('haul') ||
        q.includes('fleet') ||
        q.includes('crusher') ||
        q.includes('arrival')
      ) {
        if (isDecisionAlert) {
          answer =
            'Alert: Haul trucks are bunched at the primary crusher queue, creating a 17-minute loading delay. Rain approaches in 20 minutes. I recommend resequencing to Bench 3 to avoid waiting.';
          priority = 'HIGH';
        } else {
          answer =
            'Truck 02 is on approach to Bench 2, estimated arrival in 3 minutes. Crusher queue is currently clear with 4 active fleet haulers in the cycle.';
          priority = 'NORMAL';
        }
      }
      // 2. Safety / Seatbelt / Hazards / Slope
      else if (
        q.includes('safety') ||
        q.includes('seatbelt') ||
        q.includes('hazard') ||
        q.includes('perimeter') ||
        q.includes('slope') ||
        q.includes('clear') ||
        q.includes('safe')
      ) {
        if (safety?.seatbelt_fastened === false) {
          answer =
            'Critical Safety Alert: Seatbelt harness is unbuckled. Hydraulic circuits are locked out. Fasten your harness to resume digging.';
          priority = 'CRITICAL';
        } else if ((safety?.active_hazard_count || 0) > 0) {
          answer =
            'Proximity Warning: Support vehicle detected at 11 meters inside your 15-meter counterweight swing zone. Stop your swing immediately.';
          priority = 'CRITICAL';
        } else {
          answer =
            'Cab safety perimeter is 100% clear. Zero proximity hazards. Harness latched. Bench slope is stable at 8 degrees, well under the 15-degree safety limit.';
          priority = 'NORMAL';
        }
      }
      // 3. Pacing / Tonnage / Shift Target
      else if (
        q.includes('pace') ||
        q.includes('ton') ||
        q.includes('target') ||
        q.includes('progress') ||
        q.includes('how much') ||
        q.includes('speed')
      ) {
        const pace = twin?.productivity?.pace_percentage || 104.5;
        const volume = twin?.productivity?.completed_volume_tons || 320;
        const target = twin?.productivity?.target_volume_tons || 850;
        const progressPct = Math.round((volume / target) * 100);
        const deltaPct = Math.round(pace - 100);
        const speedText = deltaPct >= 0 ? `${deltaPct}% ahead of schedule` : `${Math.abs(deltaPct)}% behind schedule`;
        answer = `You've loaded ${volume} of your ${target}-ton shift target (${progressPct}% complete). Digging speed is ${speedText}, running at ${pace}% of planned rate.`;
        priority = 'NORMAL';
      }
      // 4. Recommendation / What to do / Next Best Action
      else if (
        q.includes('what should i do') ||
        q.includes('recommend') ||
        q.includes('what to do') ||
        q.includes('action') ||
        q.includes('delay') ||
        q.includes('options') ||
        q.includes('trajectory')
      ) {
        if (isDecisionAlert) {
          answer =
            'Tactical Advisory: Crusher queue creates a 17-minute delay before rain arrives. Say "Choose Bench 3" or tap the recovery button to resequence overburden. This saves 17 minutes and 14.8 liters of idle fuel.';
          priority = 'HIGH';
        } else if (isSafetyAlert) {
          answer =
            'Immediate safety action required: Fasten your cab harness and clear the 15-meter swing zone to restore full hydraulic power.';
          priority = 'CRITICAL';
        } else {
          const pace = twin?.productivity?.pace_percentage || 104.5;
          const deltaPct = Math.round(pace - 100);
          const speedText = deltaPct >= 0 ? `${deltaPct}% ahead of schedule` : `${Math.abs(deltaPct)}% behind schedule`;
          const remainingMins = twin?.prediction?.estimated_remaining_minutes || 145;
          answer =
            `No intervention needed. Maintain current digging speed, currently ${speedText}. Shift completion is on schedule with ${remainingMins} minutes remaining.`;
          priority = 'NORMAL';
        }
      }
      // 5. Execute Action: Choose Bench 3
      else if (
        q.includes('choose bench 3') ||
        q.includes('select bench 3') ||
        q.includes('resequence') ||
        q.includes('commit')
      ) {
        if (onChooseTrajectory) {
          onChooseTrajectory('SCEN-02-RESEQUENCE');
        }
        answer =
          'Affirmative. Committed Bench 3 recovery sequence. Dispatch routing updated. Haul queue bypassed and 14.8 liters of fuel saved. Resuming standard digging.';
        priority = 'HIGH';
      }
      // 6. View Mode Switch Commands
      else if (q.includes('switch to detail') || q.includes('show detail') || q.includes('detailed')) {
        if (onViewModeChange) onViewModeChange('DETAILED');
        answer = 'Switched to Detailed Engineering Audit view. Machine telemetry and DAG breakdown active.';
        priority = 'NORMAL';
      } else if (q.includes('switch to hud') || q.includes('show hud') || q.includes('hud mode')) {
        if (onViewModeChange) onViewModeChange('CAB_HUD');
        answer = 'Switched to Cab HUD Hands-Free mode. Large glanceable indicators active.';
        priority = 'NORMAL';
      }
      // 7. Weather / Rain
      else if (q.includes('weather') || q.includes('rain') || q.includes('saturation')) {
        answer =
          'Weather radar reports incoming overcast and rain front arriving in approximately 20 minutes. Ground saturation will rise from 12% to 28% if bench trenching is delayed.';
        priority = 'NORMAL';
      }
      // 8. General Help
      else {
        answer =
          `I heard "${query}". As your in-cab companion, you can ask me: "Where are the trucks?", "What should I do?", "Check safety perimeter", "What is my target pace?", or tell me "Choose Bench 3 path".`;
        priority = 'NORMAL';
      }

      setLastResponse(answer);
      // Explicit human question forces immediate preemption of any prior speech
      speak(answer, priority, true /* forceInterrupt */);
    },
    [dashboard, demoState, onChooseTrajectory, onViewModeChange, speak]
  );

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        setTranscript(text);
        processQuery(text);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch {
      setSpeechSupported(false);
    }
  }, [processQuery]);

  // Push-to-Talk (PTT) Spacebar Hotkey & Escape Stop Key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input or textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;

      // Escape key halts speech immediately
      if (e.key === 'Escape' && isSpeaking) {
        e.preventDefault();
        stopSpeaking();
        return;
      }

      // Spacebar Push-to-Talk
      if (e.code === 'Space' && !e.repeat && !isPTTHeld) {
        e.preventDefault();
        // If speaking, stop playback immediately when opening microphone
        stopSpeaking();
        setIsPTTHeld(true);
        playRadioSound('PTT_ON');
        if (recognitionRef.current && !isListening) {
          setTranscript('');
          try {
            recognitionRef.current.start();
          } catch {}
        }
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;
      if (e.code === 'Space' && isPTTHeld) {
        e.preventDefault();
        setIsPTTHeld(false);
        playRadioSound('PTT_OFF');
        if (recognitionRef.current && isListening) {
          try {
            recognitionRef.current.stop();
          } catch {}
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isPTTHeld, isListening, isSpeaking, stopSpeaking]);

  // Toggle Voice Recognition Listening
  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      playRadioSound('PTT_OFF');
      recognitionRef.current.stop();
    } else {
      stopSpeaking();
      setTranscript('');
      playRadioSound('PTT_ON');
      try {
        recognitionRef.current.start();
      } catch {
        // Already started or restarting
      }
    }
  };

  // Autonomous Event-Driven Voice Broadcasts with Priority Preemption
  useEffect(() => {
    if (!autoAnnounceEnabled || !voiceAudioEnabled) return;

    const currentStep = demoState?.current_step || 1;
    const currentMode = dashboard?.attention_mode || 'NORMAL';

    if (currentStep !== prevStepRef.current || currentMode !== prevAttentionModeRef.current) {
      prevStepRef.current = currentStep;
      prevAttentionModeRef.current = currentMode;

      // Speak autonomous updates when shift situation changes
      if (currentStep === 2) {
        const msg =
          'Safety Warning: Seatbelt unbuckled. Hydraulic interlock engaged. Fasten harness buckle to resume operations.';
        setLastResponse(msg);
        speak(msg, 'CRITICAL', true);
      } else if (currentStep === 3) {
        const msg =
          'Safety Alert: Object detected at 11 meters in rear swing radius. Stop swing immediately.';
        setLastResponse(msg);
        speak(msg, 'CRITICAL', true);
      } else if (currentStep === 4) {
        const msg =
          'Engine Advisory: High idle at 1800 RPM detected while waiting for trucks. Throttle back to 1000 RPM to save fuel.';
        setLastResponse(msg);
        speak(msg, 'HIGH', true);
      } else if (currentStep === 5 || currentStep === 6) {
        const msg =
          'Tactical Advisory: 17-minute delay ahead at crusher queue with incoming rain. Say "Choose Bench 3" or tap the recovery button.';
        setLastResponse(msg);
        speak(msg, 'HIGH', true);
      } else if (currentStep === 7) {
        const msg =
          'Tactical Decision Logged: Bench 3 recovery in progress. Haul bottleneck bypassed, digging speed running 18% ahead of schedule.';
        setLastResponse(msg);
        speak(msg, 'HIGH', true);
      }
    }
  }, [demoState?.current_step, dashboard?.attention_mode, autoAnnounceEnabled, voiceAudioEnabled, speak]);

  const quickPrompts = [
    { label: 'Where are the trucks?', icon: <Truck className="w-3.5 h-3.5 text-sky-400" /> },
    { label: 'What should I do about the delay?', icon: <Compass className="w-3.5 h-3.5 text-[#FFCD11]" /> },
    { label: 'Check safety perimeter', icon: <Shield className="w-3.5 h-3.5 text-emerald-400" /> },
    { label: 'What is my target pace?', icon: <TrendingUp className="w-3.5 h-3.5 text-teal-400" /> },
    { label: 'Choose Bench 3 path', icon: <Sparkles className="w-3.5 h-3.5 text-[#FFCD11]" /> },
  ];

  return (
    <div className="bg-[#181818] border-2 border-[#2D2D2D] rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
      {/* Top Header & Assistant Status */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl font-black ${
            isSpeaking ? 'bg-[#FFCD11] text-black animate-pulse' : 'bg-[#252525] text-[#FFCD11]'
          }`}>
            <Radio className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm sm:text-base font-black text-white uppercase tracking-tight">
                CAT In-Cab Voice Companion
              </h3>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider flex items-center space-x-1 ${
                isSpeaking
                  ? 'bg-[#FFCD11] text-black font-black'
                  : isListening
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full mr-1 ${
                  isSpeaking ? 'bg-black animate-ping' : isListening ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'
                }`}></span>
                <span>{isSpeaking ? 'Radio Transmitting' : isListening ? 'Listening...' : 'Voice Active'}</span>
              </span>
            </div>
            <p className="text-xs text-gray-400">
              Hands-free audio assistant • Speak naturally without looking away from the bench
            </p>
          </div>
        </div>

        {/* Voice Toggles & Mic Trigger */}
        <div className="flex items-center space-x-2 flex-wrap gap-y-2">
          {/* Stop Audio Button (Visible when speaking or anytime) */}
          {isSpeaking && (
            <button
              type="button"
              onClick={stopSpeaking}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-black text-xs transition cursor-pointer shadow-lg animate-pulse ring-2 ring-rose-500/50"
              title="Stop voice broadcast immediately (or press Escape)"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Stop Audio</span>
            </button>
          )}

          {/* Replay Transmission Button */}
          <button
            type="button"
            onClick={replayLastTransmission}
            className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border border-[#3E3E3E] bg-[#222222] hover:bg-[#2C2C2C] text-gray-300 hover:text-white text-xs font-bold transition cursor-pointer"
            title="Replay the last in-cab radio transmission"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#FFCD11]" />
            <span>Replay</span>
          </button>

          {/* Audio Output Mute Toggle */}
          <button
            type="button"
            onClick={() => {
              if (voiceAudioEnabled) {
                stopSpeaking();
                setVoiceAudioEnabled(false);
              } else {
                setVoiceAudioEnabled(true);
              }
            }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition cursor-pointer ${
              voiceAudioEnabled
                ? 'bg-[#252525] border-[#3E3E3E] text-gray-200 hover:text-white'
                : 'bg-rose-950/40 border-rose-600/60 text-rose-300'
            }`}
            title={voiceAudioEnabled ? 'Voice audio enabled (Click to mute)' : 'Voice audio muted (Click to unmute)'}
          >
            {voiceAudioEnabled ? <Volume2 className="w-4 h-4 text-emerald-400" /> : <VolumeX className="w-4 h-4 text-rose-400" />}
            <span>{voiceAudioEnabled ? 'Voice Audio: ON' : 'Audio: MUTED'}</span>
          </button>

          {/* Auto-Announce Toggle */}
          <button
            type="button"
            onClick={() => setAutoAnnounceEnabled(!autoAnnounceEnabled)}
            className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border text-xs font-bold transition cursor-pointer ${
              autoAnnounceEnabled
                ? 'bg-[#252525] border-[#3E3E3E] text-[#FFCD11]'
                : 'bg-[#1C1C1C] border-[#333333] text-gray-500'
            }`}
            title="Automatically speak shift alerts and haul delays without asking"
          >
            <span>Auto-Broadcasts: {autoAnnounceEnabled ? 'ON' : 'OFF'}</span>
          </button>

          {/* Large Push-to-Talk Mic Button */}
          <button
            type="button"
            onClick={toggleListening}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wider shadow-lg transition-all cursor-pointer ${
              isPTTHeld || isListening
                ? 'bg-rose-600 text-white animate-pulse ring-4 ring-rose-600/40 scale-105'
                : isSpeaking
                ? 'bg-[#FFCD11] text-black ring-2 ring-[#FFCD11]/50'
                : 'bg-[#2E2E2E] hover:bg-[#3D3D3D] text-white border border-[#444444]'
            }`}
            title="Click to talk, or HOLD Spacebar on your keyboard (emulates joystick trigger)"
          >
            {isPTTHeld ? (
              <>
                <Mic className="w-4 h-4 animate-bounce" />
                <span>PTT Trigger Held...</span>
              </>
            ) : isListening ? (
              <>
                <Mic className="w-4 h-4 animate-bounce" />
                <span>Listening...</span>
              </>
            ) : isSpeaking ? (
              <>
                <Volume2 className="w-4 h-4 animate-pulse" />
                <span>Radio Speaking</span>
              </>
            ) : (
              <>
                <Mic className="w-4 h-4 text-[#FFCD11]" />
                <span>PTT Mic (Hold Space)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Industrial Reliability & Acoustic Guardrails Strip */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-1.5 rounded-lg bg-[#141414] border border-[#262626] text-[11px] text-gray-400">
        <div className="flex items-center space-x-2">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span><strong>Industrial Guardrail:</strong> Joystick Push-to-Talk (Hold Space) • Stop (Esc)</span>
        </div>
        <div className="flex items-center space-x-3 text-[10px] sm:text-[11px]">
          <span className="flex items-center space-x-1">
            <Radio className="w-3 h-3 text-[#FFCD11]" />
            <span>Cab Noise Gate: <strong className="text-gray-300">78 dBA Nominal</strong></span>
          </span>
          <span>•</span>
          <span className="flex items-center space-x-1 text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Preemptive Audio Priority Active</span>
          </span>
        </div>
      </div>

      {/* Radio Dispatch Output Console */}
      <div className="bg-[#121212] border border-[#262626] rounded-xl p-3.5 sm:p-4 space-y-2">
        <div className="flex items-center justify-between text-xs flex-wrap gap-2">
          <div className="flex items-center space-x-2 text-gray-400">
            <span className={`w-2 h-2 rounded-full ${
              currentPriority === 'CRITICAL'
                ? 'bg-rose-500 animate-ping'
                : currentPriority === 'HIGH'
                ? 'bg-amber-400 animate-pulse'
                : 'bg-[#FFCD11] animate-pulse'
            }`}></span>
            <strong className="text-gray-300 font-mono text-[11px] uppercase tracking-wider">
              📻 In-Cab Radio Transmission
            </strong>

            {/* Audio Priority Indicator */}
            {currentPriority === 'CRITICAL' && (
              <span className="px-2 py-0.5 rounded bg-rose-950/90 border border-rose-500 text-rose-300 font-black text-[10px] uppercase tracking-wider animate-pulse flex items-center space-x-1">
                <AlertTriangle className="w-3 h-3 text-rose-400 mr-0.5" />
                <span>EMERGENCY PRIORITY</span>
              </span>
            )}
            {currentPriority === 'HIGH' && (
              <span className="px-2 py-0.5 rounded bg-amber-950/80 border border-amber-500/80 text-amber-300 font-black text-[10px] uppercase tracking-wider">
                TACTICAL PRIORITY
              </span>
            )}
            {currentPriority === 'NORMAL' && (
              <span className="px-2 py-0.5 rounded bg-[#1F1F1F] border border-[#333333] text-gray-400 text-[10px] uppercase tracking-wider">
                STANDARD DISPATCH
              </span>
            )}
          </div>

          {/* Inline Audio Controls (Stop / Replay) */}
          <div className="flex items-center space-x-2">
            {isSpeaking && (
              <button
                type="button"
                onClick={stopSpeaking}
                className="flex items-center space-x-1 px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] uppercase tracking-wider transition cursor-pointer shadow"
                title="Stop radio transmission immediately"
              >
                <Square className="w-3 h-3 fill-current" />
                <span>Stop (Esc)</span>
              </button>
            )}
            <button
              type="button"
              onClick={replayLastTransmission}
              className="flex items-center space-x-1 px-2 py-1 rounded bg-[#202020] hover:bg-[#2C2C2C] border border-[#333333] text-gray-300 hover:text-white text-[10px] font-bold transition cursor-pointer"
              title="Repeat last transmission"
            >
              <RotateCcw className="w-3 h-3 text-[#FFCD11]" />
              <span>Repeat</span>
            </button>
            {isSpeaking && (
              <div className="flex items-center space-x-1 pl-1">
                <span className="w-1 h-3 bg-[#FFCD11] animate-pulse"></span>
                <span className="w-1 h-5 bg-[#FFCD11] animate-pulse delay-75"></span>
                <span className="w-1 h-2 bg-[#FFCD11] animate-pulse delay-150"></span>
                <span className="w-1 h-4 bg-[#FFCD11] animate-pulse delay-100"></span>
              </div>
            )}
          </div>
        </div>

        {transcript && (
          <div className="text-xs text-sky-300 bg-sky-950/30 border border-sky-900/50 p-2 rounded-lg flex items-center space-x-2">
            <span className="text-sky-400 font-bold">You asked:</span>
            <span className="italic">"{transcript}"</span>
          </div>
        )}

        <div className="text-xs sm:text-sm text-gray-200 font-medium leading-relaxed pl-1">
          {lastResponse}
        </div>
      </div>

      {/* Quick 1-Touch Voice Queries (For high background cab noise) */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-gray-400 font-bold uppercase tracking-wider">
          <span>Hands-Free Quick Queries (1-Touch Voice Prompts):</span>
          <span className="text-gray-500 font-normal">Click to simulate speaking command</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setTranscript(p.label);
                processQuery(p.label);
              }}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#222222] hover:bg-[#2D2D2D] hover:border-[#FFCD11]/60 text-gray-300 hover:text-white border border-[#333333] text-xs font-semibold transition cursor-pointer shadow-sm"
            >
              {p.icon}
              <span>"{p.label}"</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
