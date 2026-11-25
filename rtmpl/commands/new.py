"""Initialize a research layout or create a managed project explicitly."""
from __future__ import annotations

from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import State, save_state
from ..core.template import load_manifest, walk_payload
from ..core.tx import atomic_write_bytes
from ._common import (
    CommandError,
    collect_variables,
    config_for_new,
    local_path,
    rtmpl_dir,
    save_config,
)

DIRECTORIES = ("literature", "references", "paper", "src", "experiments")
MAINTENANCE_PROMPT = (
    "参考 [Agent Maintenance](https://github.com/WncFht/agent-maintenance) 的 README 和 docs/toolchain.md，为 {target} 接入适用的维护规则与工具链。"
    "先读目标现状，按需采用三个技能及其引用、共享参考、模板、Agent Notes 规则和分层 AGENTS.md；"
    "在目标 docs/AGENTS.md 明确实际内容归属，在 docs/README.md 建立阅读入口，按需采用实验记录规则和文档检查清单，不做重复检测；"
    "按真实语言范围合并 formatter、lint、两阶段 hooks 和 CI，复用已有构建与检查入口。"
    "依赖归目标项目与锁文件，不覆盖现有规则，不复制本包的过程记录。需要 MPE 时再采用预览资源与同步入口。"
    "保留来源与许可，修复引用，验证正常与违规输入、真实部分暂存和失败传播。仅配置必要 CI，不新增自动发布；完成后说明改动与未验证项。"
)


def _scaffold(args) -> int:
    if args.var or args.force:
        raise CommandError("--var and --force require an explicit --template")

    target = Path(args.path or args.name or ".").resolve()
    if target.exists() and not target.is_dir():
        raise CommandError(f"target {target} is not a directory")

    directories = [local_path(target, name) for name in DIRECTORIES]
    for directory in directories:
        if directory.exists() and not directory.is_dir():
            raise CommandError(f"{directory} is not a directory")

    try:
        target.mkdir(parents=True, exist_ok=True)
        for directory in directories:
            try:
                directory.mkdir()
            except FileExistsError:
                if not directory.is_dir() or directory.is_symlink():
                    raise
                continue
            (directory / ".gitkeep").touch(exist_ok=False)
    except OSError as exc:
        raise CommandError(f"could not initialize {target}: {exc}") from exc

    print(f"Research directories ready at {target}")
    print("\n如需初始化文档和维护工具链，请把下面的指令交给 Agent：\n")
    print(MAINTENANCE_PROMPT.format(target=f"`{target}`"))
    return 0


def run(args) -> int:
    if args.template is None:
        return _scaffold(args)
    return _create_managed_project(args)


def _check_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise CommandError(f"target {target} is not empty (use --force to overwrite)")


def _create_managed_project(args) -> int:
    template = args.template
    manifest = load_manifest(template)
    flag_values: dict[str, str] = dict(getattr(args, "var", {}) or {})
    name = getattr(args, "name", None)
    if name and manifest.variable_for_field("proj") and "proj" not in flag_values:
        flag_values["proj"] = name
    values = collect_variables(manifest, flag_values, args.no_input)

    target = (
        Path(args.path)
        if getattr(args, "path", None)
        else Path.cwd() / (name or values.get("proj", "project"))
    )
    _check_target(target, getattr(args, "force", False))

    payload = walk_payload(template, manifest)
    rendered = rendermod.render_payload(payload, manifest, values)
    rendermod.check_render_residuals(rendered, manifest)

    target.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str | None] = {}
    for rel, data in rendered.items():
        destination = local_path(target, rel)
        atomic_write_bytes(destination, data)
        hashes[rel] = hashmod.hash_data(data)

    save_config(target, config_for_new(template, values))
    save_state(rtmpl_dir(target), State(template_version=manifest.version, hashes=hashes))

    print(
        f"Created project at {target} "
        f"(template {template} @ {manifest.version}, {len(hashes)} files)"
    )
    return 0
