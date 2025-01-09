import PocketBase from 'pocketbase';
import { env } from '$env/dynamic/public';
import type { MyPocketBase } from '$types/pocketBase';

const DB_URL = env.PUBLIC_DB_URL;

const pb = new PocketBase(DB_URL) as MyPocketBase;

pb.autoCancellation(false);

export { pb };
