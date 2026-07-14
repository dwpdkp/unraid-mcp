"""Per-action Unraid tools.

Alternative registration to the single consolidated `unraid` tool
(`register_unraid_tool` in `unraid.py`). Exposes each of the 19 actions as its
own MCP tool (`unraid_system`, `unraid_docker`, `unraid_array`, ...) so a
client can call `unraid_docker(subaction="list")` instead of
`unraid(action="docker", subaction="list")`.

Each wrapper takes only the parameters relevant to its action (mirroring the
narrow keyword sets already used by the `_dispatch_*` adapters in `unraid.py`)
and calls the same underlying `_handle_*` functions — no business logic is
duplicated or reimplemented here.

This trades a larger tool count for a smaller, action-scoped per-tool schema.
Only one of `register_unraid_tool` / `register_unraid_action_tools` should be
active at a time (selected in `server.py`) — running both would expose the
same operations twice under different names.
"""

from typing import Any

from fastmcp import Context, FastMCP

from ._array import _handle_array
from ._connect import _handle_connect
from ._customization import _handle_customization
from ._disk import _handle_disk
from ._docker import _handle_docker
from ._key import _handle_key
from ._live import _handle_live
from ._notification import _handle_notification
from ._oidc import _handle_oidc
from ._onboarding import _handle_onboarding
from ._plugin import _handle_plugin
from ._rclone import _handle_rclone
from ._setting import _handle_setting
from ._system import _handle_system
from ._user import _handle_user
from ._vm import _handle_vm
from .unraid import _HELP_TEXT, _handle_health


def register_unraid_action_tools(mcp: FastMCP) -> None:
    """Register one MCP tool per Unraid action (19 tools + help)."""

    @mcp.tool(timeout=120)
    async def unraid_system(
        subaction: str,
        device_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | str:
        """Server info, metrics, network, UPS (25 subactions).

        Subactions: overview, array, network, registration, variables, metrics,
        network_metrics, services, display, display_details, config, online,
        owner, settings, server, server_details, servers, network_access_urls,
        flash, ups_devices, ups_device, ups_config, server_time, timezones,
        network_interfaces.
        """
        return await _handle_system(subaction, device_id=device_id, limit=limit)

    @mcp.tool(timeout=120)
    async def unraid_health(
        subaction: str,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Health checks, connection test, diagnostics, setup (4 subactions).

        Subactions: check, test_connection, diagnose, setup.
        """
        return await _handle_health(subaction, ctx)

    @mcp.tool(timeout=120)
    async def unraid_array(
        subaction: str,
        disk_id: str | None = None,
        correct: bool | None = None,
        slot: int | None = None,
        confirm: bool = False,
        limit: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Parity checks, array state, disk operations (14 subactions).

        Subactions: parity_status, parity_history, assignable_disks,
        parity_start, parity_pause, parity_resume, parity_cancel, start_array,
        stop_array*, add_disk, remove_disk*, mount_disk, unmount_disk,
        clear_disk_stats*. (* destructive — requires confirm=True)
        """
        return await _handle_array(
            subaction,
            disk_id=disk_id,
            correct=correct,
            slot=slot,
            ctx=ctx,
            confirm=confirm,
            limit=limit,
        )

    @mcp.tool(timeout=120)
    async def unraid_disk(
        subaction: str,
        disk_id: str | None = None,
        log_path: str | None = None,
        tail_lines: int = 100,
        remote_name: str | None = None,
        source_path: str | None = None,
        destination_path: str | None = None,
        backup_options: dict[str, Any] | None = None,
        confirm: bool = False,
        level: str | None = None,
        context: int = 2,
        limit: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Shares, physical disks, log files (6 subactions).

        Subactions: shares, disks, disk_details, log_files, logs, flash_backup*.
        (* destructive — requires confirm=True)
        """
        return await _handle_disk(
            subaction,
            disk_id=disk_id,
            log_path=log_path,
            tail_lines=tail_lines,
            remote_name=remote_name,
            source_path=source_path,
            destination_path=destination_path,
            backup_options=backup_options,
            ctx=ctx,
            confirm=confirm,
            level=level,
            context=context,
            limit=limit,
        )

    @mcp.tool(timeout=120)
    async def unraid_docker(
        subaction: str,
        container_id: str | None = None,
        network_id: str | None = None,
        limit: int = 20,
        confirm: bool = False,
        container_ids: list[str] | None = None,
        with_image: bool = False,
        autostart_entries: list[dict[str, Any]] | None = None,
        organizer_input: dict[str, Any] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Container lifecycle, updates, organizer, networks (26 subactions).

        Subactions: list, details, logs, ports, start, stop, restart, unpause,
        networks, network_details, remove_container*, update_container,
        update_containers, update_all_containers, update_autostart,
        refresh_digests, sync_template_paths, reset_template_mappings*,
        create_folder, create_folder_with_items, rename_folder,
        set_folder_children, delete_entries*, move_entries_to_folder,
        move_items_to_position, update_view_preferences.
        (* destructive — requires confirm=True)
        """
        return await _handle_docker(
            subaction,
            container_id=container_id,
            network_id=network_id,
            limit=limit,
            ctx=ctx,
            confirm=confirm,
            container_ids=container_ids,
            with_image=with_image,
            autostart_entries=autostart_entries,
            organizer_input=organizer_input,
        )

    @mcp.tool(timeout=120)
    async def unraid_vm(
        subaction: str,
        vm_id: str | None = None,
        confirm: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Virtual machine lifecycle (9 subactions).

        Subactions: list, details, start, stop, pause, resume, force_stop*,
        reboot, reset*. (* destructive — requires confirm=True)
        """
        return await _handle_vm(subaction, vm_id=vm_id, ctx=ctx, confirm=confirm)

    @mcp.tool(timeout=120)
    async def unraid_notification(
        subaction: str,
        confirm: bool = False,
        notification_id: str | None = None,
        notification_ids: list[str] | None = None,
        notification_type: str | None = None,
        importance: str | None = None,
        offset: int = 0,
        limit: int = 20,
        list_type: str = "UNREAD",
        title: str | None = None,
        subject: str | None = None,
        description: str | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """System notifications CRUD (13 subactions).

        Subactions: overview, list, create, notify_if_unique, archive,
        mark_unread, recalculate, archive_all, archive_many, unarchive_many,
        unarchive_all, delete*, delete_archived*.
        (* destructive — requires confirm=True)
        """
        return await _handle_notification(
            subaction,
            ctx=ctx,
            confirm=confirm,
            notification_id=notification_id,
            notification_ids=notification_ids,
            notification_type=notification_type,
            importance=importance,
            offset=offset,
            limit=limit,
            list_type=list_type,
            title=title,
            subject=subject,
            description=description,
        )

    @mcp.tool(timeout=120)
    async def unraid_key(
        subaction: str,
        key_id: str | None = None,
        name: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        permissions_input: list[dict[str, Any]] | None = None,
        confirm: bool = False,
        limit: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """API key & permission management (13 subactions).

        Subactions: list, get, possible_roles, possible_permissions,
        permissions_for_roles, preview_permissions, auth_actions,
        creation_form_schema, create, update, delete*, add_role, remove_role.
        (* destructive — requires confirm=True)
        """
        return await _handle_key(
            subaction,
            key_id=key_id,
            name=name,
            roles=roles,
            permissions=permissions,
            ctx=ctx,
            confirm=confirm,
            limit=limit,
            permissions_input=permissions_input,
        )

    @mcp.tool(timeout=120)
    async def unraid_plugin(
        subaction: str,
        names: list[str] | None = None,
        bundled: bool = False,
        restart: bool = True,
        url: str | None = None,
        plugin_name: str | None = None,
        forced: bool = False,
        operation_id: str | None = None,
        confirm: bool = False,
        limit: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Plugin management and async installs (8 subactions).

        Subactions: list, installed_unraid, install_operations,
        install_operation, add, remove*, install*, install_language*.
        (* destructive — requires confirm=True)
        """
        return await _handle_plugin(
            subaction,
            names=names,
            bundled=bundled,
            restart=restart,
            ctx=ctx,
            confirm=confirm,
            limit=limit,
            url=url,
            plugin_name=plugin_name,
            forced=forced,
            operation_id=operation_id,
        )

    @mcp.tool(timeout=120)
    async def unraid_rclone(
        subaction: str,
        name: str | None = None,
        provider_type: str | None = None,
        config_data: dict[str, Any] | None = None,
        confirm: bool = False,
        limit: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Cloud storage remote management (4 subactions).

        Subactions: list_remotes, config_form, create_remote, delete_remote*.
        (* destructive — requires confirm=True)
        """
        return await _handle_rclone(
            subaction,
            name=name,
            provider_type=provider_type,
            config_data=config_data,
            ctx=ctx,
            confirm=confirm,
            limit=limit,
        )

    @mcp.tool(timeout=120)
    async def unraid_setting(
        subaction: str,
        settings_input: dict[str, Any] | None = None,
        ups_config: dict[str, Any] | None = None,
        config_input: dict[str, Any] | None = None,
        name: str | None = None,
        comment: str | None = None,
        sys_model: str | None = None,
        confirm: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """System settings, UPS, SSH, time, identity (6 subactions).

        Subactions: update, configure_ups*, update_ssh*, update_temperature,
        update_system_time*, update_server_identity.
        (* destructive — requires confirm=True)
        """
        return await _handle_setting(
            subaction,
            settings_input=settings_input,
            ups_config=ups_config,
            ctx=ctx,
            confirm=confirm,
            config_input=config_input,
            name=name,
            comment=comment,
            sys_model=sys_model,
        )

    @mcp.tool(timeout=120)
    async def unraid_connect(
        subaction: str,
        connect_input: dict[str, Any] | None = None,
        confirm: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """Unraid Connect / remote access (8 subactions).

        Subactions: remote_access, cloud, status, update_api_settings*,
        sign_in*, sign_out*, setup_remote_access*, enable_dynamic_remote_access*.
        (* destructive — requires confirm=True)
        """
        return await _handle_connect(subaction, ctx=ctx, confirm=confirm, connect_input=connect_input)

    @mcp.tool(timeout=120)
    async def unraid_onboarding(
        subaction: str,
        onboarding_input: dict[str, Any] | None = None,
        confirm: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any] | str:
        """First-boot/onboarding state (11 subactions).

        Subactions: internal_boot_context, complete, open, close, resume,
        bypass, reset*, set_override, clear_override,
        refresh_internal_boot_context, create_internal_boot_pool*.
        (* destructive — requires confirm=True)
        """
        return await _handle_onboarding(
            subaction, ctx=ctx, confirm=confirm, onboarding_input=onboarding_input
        )

    @mcp.tool(timeout=120)
    async def unraid_customization(
        subaction: str,
        theme_name: str | None = None,
        locale: str | None = None,
    ) -> dict[str, Any] | str:
        """Theme, locale and UI customization (6 subactions).

        Subactions: public_theme, is_initial_setup, sso_enabled, details,
        set_theme, set_locale.
        """
        return await _handle_customization(subaction, theme_name=theme_name, locale=locale)

    @mcp.tool(timeout=120)
    async def unraid_oidc(
        subaction: str,
        provider_id: str | None = None,
        token: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | str:
        """OIDC/SSO provider management (5 subactions).

        Subactions: providers, provider, configuration, public_providers,
        validate_session.
        """
        return await _handle_oidc(subaction, provider_id=provider_id, token=token, limit=limit)

    @mcp.tool(timeout=120)
    async def unraid_user(subaction: str = "me") -> dict[str, Any] | str:
        """Current authenticated user (1 subaction: me)."""
        return await _handle_user(subaction)

    @mcp.tool(timeout=120)
    async def unraid_live(
        subaction: str,
        path: str | None = None,
        collect_for: float = 5.0,
        timeout: float = 10.0,  # noqa: ASYNC109
        level: str | None = None,
        context: int = 2,
        limit: int = 20,
        operation_id: str | None = None,
    ) -> dict[str, Any] | str:
        """Real-time WebSocket subscription snapshots (17 subactions).

        Subactions: cpu, memory, cpu_telemetry, array_state, parity_progress,
        ups_status, notifications_overview, notifications_warnings,
        notification_feed, log_tail (requires path=), owner, server_status,
        display, docker_container_stats, temperature, network_metrics,
        plugin_install_updates.
        """
        return await _handle_live(
            subaction,
            path=path,
            collect_for=collect_for,
            timeout=timeout,
            level=level,
            context=context,
            limit=limit,
            operation_id=operation_id,
        )

    @mcp.tool(timeout=120)
    async def unraid_subscriptions(
        subaction: str,
        subscription_query: str | None = None,
    ) -> dict[str, Any] | str:
        """WebSocket subscription diagnostics (2 subactions).

        Subactions: diagnose, test_query (requires subscription_query=).
        """
        # Lazy import to keep tool import-time free of the subscription stack
        # (mirrors the pattern used by the consolidated `unraid` tool).
        from ..subscriptions.diagnostics import _handle_subscriptions

        return await _handle_subscriptions(subaction, subscription_query)

    @mcp.tool(timeout=120)
    async def unraid_help() -> str:
        """Return the full Markdown action/subaction reference for these tools."""
        return _HELP_TEXT
