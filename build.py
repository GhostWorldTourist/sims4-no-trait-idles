"""No Trait Idles - build script.

Many traits come with an idle animation: Mystical, Goofball, Gloomy, Paranoid,
Cheerful and so on. The Sim plays it whenever they have nothing better to do.
This stops all of them. The traits themselves are untouched - their buffs, whims,
socials, moodlets and autonomy all still work - only the idle animation is gone.

How this works
--------------
Each trait idle is a MixerInteraction named `Idle_Trait_*`, offered by the
trait's buff (`interactions.interaction_items`) and picked by mixer autonomy
from the IDLES group. `_MixerAutonomy._aop_pre_tests` calls `_allow_autonomous`,
which rejects any affordance with `allow_autonomous` False when the request
comes from autonomy. Trait idles already have `allow_user_directed` False, so
with both off nothing can start them.

Overriding the idle mixers rather than the trait buffs leaves the buffs - where
the gameplay lives, and where other trait mods do their work - alone. No script,
so nothing runs during play.

Scope: every MixerInteraction whose name starts `idle_trait_` (any case) in
the installed game, found at build time so new packs are picked up on
rebuild. Horse and pet idles are left out on purpose: for animals the idle is how
the trait shows at all. So is any idle another installed mod already overrides
(see OWNED_ELSEWHERE).

Author: GhostWorldTourist
"""
import glob, os, re, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.environ['LOCALAPPDATA'], 'sulskill', 'ts4-knowledge', 'lib'))
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'repos', 'sulskill', 'sulskill-modbuild', 'scripts'))
import mergedtuning, dbpf

GAME = r'C:\Games\The Sims 4'
T_INTERACTION = 0xE882D22F
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'GhostWorldTourist_NoTraitIdles.package')

NAME = re.compile(r'^idle_trait_', re.I)
ANIMALS = re.compile(r'^idle_trait_(horse_|pet_)', re.I)

# Overridden by chingyu's Traits Remade In CAS (toddlerhood). Two overrides at
# the same priority have no defined winner, so leave this one to that mod.
OWNED_ELSEWHERE = {'Idle_Trait_Happy_Toddler'}


def sources():
    # DeltaBuild outranks FullBuild, so read the delta for each pack and only
    # fall back to the full build for what the delta does not carry.
    deltas = [os.path.join(GAME, r'Data\Simulation\SimulationDeltaBuild0.package')]
    deltas += sorted(glob.glob(os.path.join(GAME, r'Delta\*\SimulationDeltaBuild0.package')))
    fulls = [os.path.join(GAME, r'Data\Simulation\SimulationFullBuild0.package')]
    fulls += sorted(glob.glob(os.path.join(GAME, r'EP*\SimulationFullBuild0.package')))
    fulls += sorted(glob.glob(os.path.join(GAME, r'GP*\SimulationFullBuild0.package')))
    fulls += sorted(glob.glob(os.path.join(GAME, r'SP*\SimulationFullBuild0.package')))
    return deltas + fulls


def disable(elem):
    node = elem.find("T[@n='allow_autonomous']")
    if node is None:
        node = ET.SubElement(elem, 'T', n='allow_autonomous')
    node.text = 'False'
    ud = elem.find("T[@n='allow_user_directed']")
    if ud is None or ud.text != 'False':
        raise SystemExit('%s can be started by the player; it is not a plain '
                         'idle - review before rebuilding' % elem.get('n'))
    elem[:] = sorted(elem, key=lambda e: e.get('n', ''))


def main():
    found, skipped = {}, set()
    for pkg in sources():
        for _, _, ct in mergedtuning.iter_resources(pkg):
            for inst in ct.instances():
                n = inst.attrs.get('n', '')
                if inst.res_type != 'interaction' or not NAME.match(n):
                    continue
                if inst.attrs.get('c') != 'MixerInteraction':
                    continue
                if ANIMALS.match(n) or n in OWNED_ELSEWHERE:
                    skipped.add(n)
                    continue
                iid = int(inst.attrs['s'])
                if iid not in found:
                    found[iid] = ct.expand(inst)
    resources = []
    for iid, elem in sorted(found.items(), key=lambda kv: kv[1].get('n').lower()):
        disable(elem)
        xml = b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(elem, encoding='utf-8')
        resources.append((T_INTERACTION, 0, iid, xml))
        print('  %s' % elem.get('n'))
    print('\nleft alone (animals, owned elsewhere): %d' % len(skipped))
    n, size = dbpf.write(OUT, resources)
    print('wrote %s\n  %d resources, %d bytes' % (OUT, n, size))
    return 0


if __name__ == '__main__':
    sys.exit(main())
