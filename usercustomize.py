import minukimi_v09

try:
    from minukimi_v10 import apply_v10
    apply_v10()
except Exception as exc:
    print('MINUKIMI v1.0 overlay failed:', repr(exc))

try:
    import minukimi_v11
except Exception as exc:
    print('MINUKIMI v1.1 product shell failed:', repr(exc))
