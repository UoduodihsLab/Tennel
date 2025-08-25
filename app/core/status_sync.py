from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.constants.enum import ScheduleStatus, TaskStatus
from app.crud.account import AccountCRUD
from app.crud.schedule import ScheduleCRUD
from app.crud.task import TaskCRUD
from .telegram_client import ClientManager


async def launch_accounts(client_manager: ClientManager):
    authenticated_accounts = await AccountCRUD().list_authenticated()
    for account in authenticated_accounts:
        if not await client_manager.is_online(account.session_name):
            await client_manager.connect_client(account.session_name)
            await AccountCRUD().update(account.id, {'online': True})


async def unlaunch_accounts(client_manager: ClientManager):
    online_accounts = await AccountCRUD().list_online()
    for account in online_accounts:
        await client_manager.remove_client(account.session_name)
        await AccountCRUD().update(account.id, {'online': False})


async def stop_schedules(scheduler: AsyncIOScheduler):
    schedules = await ScheduleCRUD().all()
    for schedule in schedules:
        job = scheduler.get_job(f'{schedule.id}')
        if job:
            scheduler.pause_job(job.id)
            scheduler.remove_job(job.id)
        await ScheduleCRUD().update(schedule.id, {'status': ScheduleStatus.PENDING})

    scheduler.pause_job('sync_channels')
    scheduler.remove_job('sync_channels')

    scheduler.pause_job('sync_accounts_online_status')
    scheduler.remove_job('sync_accounts_online_status')


async def stop_tasks():
    await TaskCRUD().update_by_status(TaskStatus.RUNNING, {'status': TaskStatus.FAILED})
