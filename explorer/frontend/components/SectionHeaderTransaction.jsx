import CustomImage from './CustomImage';
import ValueTimestamp from './ValueTimestamp';
import styles from '@/styles/components/SectionHeaderTransaction.module.scss';
import { createPageHref } from '@/utils';
import Link from 'next/link';

const SectionHeaderTransaction = ({ height, timestamp }) => {
	return (
		<Link className={styles.valueBlockHeight} href={createPageHref('blocks', height)}>
			<CustomImage className={styles.icon} src="/images/icon-transaction-header-block.svg" alt="Block" />
			<div>
				<div className={styles.title}>{height}</div>
				<ValueTimestamp value={timestamp} hasTime />
			</div>
		</Link>
	);
};

export default SectionHeaderTransaction;
