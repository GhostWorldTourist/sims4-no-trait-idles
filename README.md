# No Trait Idles

Sims stop doing the idle animations that come with their traits: Mystical's
cosmic gesturing, Goofball's antics, Gloomy's sighing and the rest. The traits
otherwise work exactly as before. Buffs, moodlets, whims, socials and autonomy
are all untouched. Only the idle animation is gone.

## How

Every trait idle is a mixer named `Idle_Trait_*` that the trait's buff gives
the Sim, and that autonomy plays when the Sim is idle. Players can't trigger
them; only autonomy can. This mod turns autonomy off for each one, so nothing
can start them. `build.py` has the detail.

- Tuning only, no script. Nothing runs during play.
- 57 idle overrides. The trait buffs themselves are left alone.
- Not included:
  - **Horse and pet idles.** For animals the idle is how the trait shows at all.
  - **`Idle_Trait_Happy_Toddler`.** chingyu's Traits Remade In CAS overrides it
    too, and with two mods overriding the same thing there's no telling which
    one wins.
- Traits added by other mods have their own idles, and this does not reach them.

## Build

```
py build.py
```

Finds every trait idle in the installed game, including any added by a new pack,
and writes `GhostWorldTourist_NoTraitIdles.package`.

Author: GhostWorldTourist
