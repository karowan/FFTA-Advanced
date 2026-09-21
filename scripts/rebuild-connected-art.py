"""Rebuild the connected preview from the authenticated corrected gameplay base.

Reuse the verified eight-stage gameplay rebuild. Rebuild every art stage and
palette hook from source/pinned imagegen inputs, then require exact tested ROM
bytes. No emulation, image generation, player saves or installed package writes.
"""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
from native_art import ROOT, sha


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def build():
    index = ROOT/'build/art/connected/current.json'
    original = json.loads(index.read_text(encoding='utf-8'))
    expected = Path(original['path']).read_bytes()
    assert hashlib.sha1(expected).hexdigest() == original['romSha1']
    out = ROOT/'build/art/connected/full-rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    # Subordinate builders have historical index outputs. Preserve those exact
    # bytes; only the final connected candidate is refreshed after equality.
    pointers = [ROOT/'build/art/clean-chain/current.json',
                ROOT/'build/art/live-palette/status-current.json']
    before = {p: p.read_bytes() for p in pointers}
    checks = []
    try:
        chain = module('connected_clean_base', 'build-clean-art-chain.py').build()
        from generated_action_transport import build as action_build
        portraits = chain['components']['portraits']
        actions = action_build(Path(portraits['path']).parent/'manifest.json',
                               publish_current=False,
                               animation_plan=ROOT/'src/art/imagegen/samurai-refined-transport.json')
        assert actions['romSha1'] == original['components']['actions']['romSha1']
        checks.append('Clean-base resource/class/portrait/action stages reproduce the tested parent')
        palette_builder = module('connected_palette_rebuild', 'build-live-art-palette.py')
        palette_builder.PARENT = Path(actions['path']).parent/'manifest.json'
        live = original['components']['livePalette']
        assert live['compactBattleStatus'] and live['compactUsKeyboard'] and not live['traceTarget']
        palette = palette_builder.build(history_slots=20, all_classes=True,
            workspace_low_address=True, provisional_history=True, fast_rotation=True,
            owned_menu_buffer=True, shared_battle_menu_heap=True,
            compact_us_keyboard=True, compact_battle_status=True)
        assert palette['romSha1'] == live['romSha1']
        checks.append('All current palette/workspace/menu hooks compile and reproduce exact tested bytes')
        assembled = module('connected_final_rebuild', 'build-connected-art.py').build(
            Path(palette['path']).parent/'manifest.json', publish_current=False,
            fixture_source=chain['fixtureSource'])
        assert assembled['romSha1'] == original['romSha1']
        assert Path(assembled['path']).read_bytes() == expected
        checks.append('Status/equipment/weapon/impact stages reproduce the entire tested connected ROM')
        # A source rebuild can change provenance paths while preserving ROM
        # bytes. Publish the new exact parent pin only after full equality.
        index.write_text(json.dumps(assembled, indent=2)+'\n', encoding='utf-8')
        report = dict(status='passed', romSha1=assembled['romSha1'], checks=checks,
            gameplayRebuild=chain['sourceRebuild'], candidateManifest=str(index),
            candidateManifestSha256=sha(index.read_bytes()),
            scope='Complete current art-stage rebuild from authenticated corrected gameplay source-build result and pinned imagegen inputs. All current palette/menu hooks compile; final ROM byte-exact. Unchanged gameplay rebuild is authenticated and reused, not rerun. Does not regenerate images, execute gameplay, install or accept final art.')
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(dict(status='passed', romSha1=assembled['romSha1'],
                              checks=len(checks), report=str(out/'report.json'))))
        return report
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',
            error=str(error), checks=checks), indent=2)+'\n', encoding='utf-8')
        print('Artifacts: '+str(out))
        raise
    finally:
        for path, raw in before.items():
            path.write_bytes(raw)


if __name__ == '__main__':
    build()
