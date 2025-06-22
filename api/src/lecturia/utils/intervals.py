from intervaltree import IntervalTree

from ..models import Event, EventList


def _collect_pose_ranges(
    events: list[Event],
    pose: str,
    target: str
) -> list[tuple[float,float]]:
    """pose 開始～次 pose で閉じる半開区間 [s,e) を抽出"""
    out: list[tuple[float,float]] = []
    open_t: float | None = None
    for ev in events:
        if ev.type != "pose" or ev.target != target:
            continue
        if ev.name == pose and open_t is None:
            open_t = ev.time_sec
        elif open_t is not None:
            out.append((open_t, ev.time_sec))
            open_t = None
    if open_t is not None:
        out.append((open_t, float("inf")))      # 末尾まで開放されなかった場合
    return out


def _ranges_to_tree(ranges: list[tuple[float,float]]) -> IntervalTree:
    """[(s,e),…] → IntervalTree([s,e))"""
    return IntervalTree.from_tuples(ranges)


def rewrite_talk_with_intervaltree(
    evlist: EventList,
    nonsilent_ranges: list[tuple[float,float]],
    targets: list[str],
) -> EventList:
    """
    各 target ごとに発話区間を置換。pose 以外は完全保持。
    """
    events = list(evlist.events)
    preserved: list[tuple[int, Event]] = []

    for idx, ev in enumerate(events):
        if ev.type == "pose" and ev.target in targets and ev.name in ("talk","idle"):
            continue
        preserved.append((idx, ev))

    new_events: list[tuple[int|None, Event]] = []    # (index,None) は新規
    for tgt in targets:
        talk_orig   = _collect_pose_ranges(events, "talk" , tgt)
        point_block = _collect_pose_ranges(events, "point", tgt)
        # IntervalTree 構築
        talk_tree   = _ranges_to_tree(talk_orig)
        detect_tree = _ranges_to_tree(nonsilent_ranges)
        point_tree  = _ranges_to_tree(point_block)
        # 和 → 差
        final_tree  = (talk_tree | detect_tree) - point_tree
        final_tree.merge_overlaps()      # 隣接・重複を統合
        # 各区間から talk / idle を生成
        for iv in sorted(final_tree):
            s, e = iv.begin, iv.end
            new_events += [
                (None, Event(type="pose", name="talk", time_sec=s, target=tgt)),
                (None, Event(type="pose", name="idle", time_sec=e, target=tgt)),
            ]

    merged = preserved + new_events
    merged.sort(key=lambda p: p[1].time_sec)
    return EventList(events=[ev for _, ev in merged])
