import { createContext } from 'svelte';
import toast from 'svelte-french-toast';
import { _ } from 'svelte-i18n';
import { get } from 'svelte/store';

import type { End, GraphEvent, Scenario, Session, Side } from '$types/pocketBase/TableTypes';
import type { MyPocketBase } from '$types/pocketBase';
import type { UnsubscribeFunc } from 'pocketbase';

const t = get(_);

export type AdminInfo = {
	isAdmin: false;
	events: null;
	ends: null;
} | {
	isAdmin: true;
	events: GraphEvent[];
	ends: End[];
}

export type UserSessionProfile = {
	readonly admin: AdminInfo['isAdmin'];
	readyToJoin: boolean;

	choosedSideId: string | null;
	pseudo: string | null;
}

export class CurrentSessionStore {
	session: Session = $state()!;
	
	unsub: Promise<UnsubscribeFunc> | null = null;

	/* Info about the user for the specific session (based on admin and localstorage) */
	sessionProfile: UserSessionProfile = $state()!;
	readonly userCanAccess: boolean = $derived(
		Boolean((this.sessionProfile?.admin || (this.sessionProfile?.choosedSideId && this.sessionProfile?.pseudo)))
	);
	/**
	 * User explicitly clicked on "Start" on the prologue
	 */
	userWantAccess: boolean = $state(false);

	readonly admin: AdminInfo;
	readonly pb: MyPocketBase;
	readonly scenario: Scenario;
	readonly sides: Side[];
	readonly ai: boolean;

	constructor(pb: MyPocketBase,
		session: Session,
		scenario: Scenario,
		admin: AdminInfo,
		sides: Side[],
		ai: boolean,
	) {
		this.pb = pb;
		this.session = session;
		this.scenario = scenario;
		this.admin = admin;
		this.sides = sides;
		this.ai = ai;

		this.sessionProfile = {
			admin: this.admin.isAdmin,
			readyToJoin: false,
			pseudo: localStorage.getItem('pseudo_' + session.id) || null,
			choosedSideId: localStorage.getItem('sideId_' + session.id) || null
		};

		this.init();
	}

	init() {
		this.unsub = this.pb.collection('Session').subscribe(this.session.id, async (res) => {
			if (!res.record || !res.record.completed) return;
			try {
				const end = await this.pb
					.collection('End')
					.getOne(res.record.end ?? '');
				this.session.completed = res.record.completed;
				this.session.end = res.record.end;

				this.session.expand = this.session.expand
					? {
						...this.session.expand,
						...end,
					}
					: {};
				toast.success(t('sessions.sessionIsOver'), {
					position: 'top-left',
				});
			} catch (e) {
				console.error(e);
				// TODO: translate
				toast.error('Error while fetching data end session', {
					position: 'top-left',
				});
			}
		});
	}

	setSide(sideId: string) {
		// TODO: validate
		this.sessionProfile.choosedSideId = sideId;
		localStorage.setItem('sideId_' + this.session.id, sideId);

		toast.success(t('side.sideSaved'), {
			position: 'bottom-center'
		});
	}
	setPseudo(pseudo: string) {
		// TODO: validate
		this.sessionProfile.pseudo = pseudo;
		localStorage.setItem('pseudo_' + this.session.id, pseudo);

		toast.success(t('side.pseudoSaved'), {
			position: 'bottom-center'
		});
	}
}

export const [getCurrentSessionCtx, setCurrentSessionCtx] = createContext<CurrentSessionStore>();