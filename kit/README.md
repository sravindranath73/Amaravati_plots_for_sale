# Kit for updating this site (for Claude)

The working files for this map are stored encrypted in `kit_state.enc` (repository root).
To restore them in a new chat, the owner supplies the site password. Then:

```bash
curl -sSL -o /tmp/r.zip https://codeload.github.com/sravindranath73/Amaravati_plots_for_sale/zip/refs/heads/main
cd /tmp && rm -rf repo && mkdir repo && cd repo && unzip -q ../r.zip && cd */
python3 kit/bootstrap.py "$PWD" '<password>'
```

then follow `/home/claude/kit/HANDOFF_NOTE.md`. `kit/map_tiles/` holds the stitched master-plan map
(public CRDA land-use map) that new plot screenshots are matched against.
