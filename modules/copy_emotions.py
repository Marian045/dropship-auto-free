def make_emotional_copy(title, raw, benefits):
    bullets = benefits or ["Comfort that calms your day", "Effortless style", "Soft on skin"]
    bl = "\n".join([f"• {b}" for b in bullets])
    return f"""{title}: the feeling you reach for.

Slip into confidence. Breathe easier. Move like yourself again.
{bl}

Because clothes shouldn’t shout—they should listen, soften, and carry you into a better day.

— Ready when you are.
"""
