import PocketBase from 'pocketbase';
import type { MyPocketBase } from '$types/pocketBase';
import { env } from '$env/dynamic/private';

const DB_URL = env.DB_URL;

export const createPocketBase = () => new PocketBase(DB_URL) as MyPocketBase;
